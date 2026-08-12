"""Confined, create-only storage primitives for the P04 coordinator.

Artifact paths are canonical repository-style relative POSIX paths.  Directory
file descriptors plus ``O_NOFOLLOW`` keep resolution beneath one explicit
artifact root.  Immutable files are staged in the destination directory,
fsynced, then installed with a no-replace hard link so readers never observe a
partial artifact and an existing receipt is never overwritten.
"""

from __future__ import annotations

import hashlib
import os
import re
import secrets
import stat
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterator

from experiments.ecdlp_lab.core.canonical import (
    canonical_json_bytes,
    strict_loads,
)

try:  # Advisory writer locks are deliberately a POSIX-only P04 primitive.
    import fcntl as _fcntl
except ImportError:  # pragma: no cover - native Windows must fail closed.
    _fcntl = None


_LOCK_NAME_RE = re.compile(r"[a-z0-9][a-z0-9_.-]{0,63}\Z")
_SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
_RESERVED_COMPONENTS = frozenset({".locks"})
_OPEN_BASE = os.O_CLOEXEC if hasattr(os, "O_CLOEXEC") else 0
_NOFOLLOW = os.O_NOFOLLOW if hasattr(os, "O_NOFOLLOW") else 0
_DIRECTORY = os.O_DIRECTORY if hasattr(os, "O_DIRECTORY") else 0


class StorageError(ValueError):
    """A storage operation is unsafe, malformed, or failed closed."""


class StorageUnavailable(StorageError):
    """The host lacks a primitive required for safe P04 storage."""


class ArtifactExists(StorageError):
    """A create-only artifact already exists."""


class ArtifactCorrupt(StorageError):
    """An artifact is noncanonical, oversized, linked, or digest-mismatched."""


class WriterLockBusy(StorageError):
    """Another coordinator currently owns the requested writer lock."""


@dataclass(frozen=True)
class StoredArtifact:
    relative_path: str
    sha256: str
    size_bytes: int


@dataclass(frozen=True)
class AppendedRecord:
    relative_path: str
    offset: int
    size_bytes: int
    sha256: str


def storage_primitives_available() -> bool:
    return (
        os.name == "posix"
        and _fcntl is not None
        and _NOFOLLOW != 0
        and _DIRECTORY != 0
        and os.open in os.supports_dir_fd
        and os.mkdir in os.supports_dir_fd
        and os.link in os.supports_dir_fd
        and os.unlink in os.supports_dir_fd
        and os.stat in os.supports_dir_fd
    )


def _exact_positive(value: Any, name: str) -> int:
    if type(value) is not int or not 1 <= value <= (1 << 50):
        raise StorageError(f"{name} must be an exact positive bounded integer")
    return value


def _relative_parts(value: Any, *, internal: bool = False) -> tuple[str, ...]:
    if type(value) is not str or not value or "\x00" in value or "\\" in value:
        raise StorageError("artifact path must be a nonempty relative POSIX path")
    pure = PurePosixPath(value)
    parts = pure.parts
    if (
        pure.is_absolute()
        or not parts
        or any(part in {"", ".", ".."} for part in parts)
        or value != "/".join(parts)
    ):
        raise StorageError("artifact path is not canonical or escapes its root")
    if not internal and any(part in _RESERVED_COMPONENTS for part in parts):
        raise StorageError("artifact path uses a reserved storage component")
    return parts


def _write_all(descriptor: int, payload: bytes) -> None:
    view = memoryview(payload)
    while view:
        written = os.write(descriptor, view)
        if written <= 0:
            raise StorageError("short write while retaining an artifact")
        view = view[written:]


def _absolute_path(value: Path | str, name: str) -> Path:
    try:
        text = os.fspath(value)
    except TypeError as error:
        raise StorageError(f"{name} must be a path") from error
    if (
        type(text) is not str
        or not text
        or "\x00" in text
        or "\\" in text
        or not text.startswith("/")
        or text == "/"
        or text.endswith("/")
        or any(component in {"", ".", ".."} for component in text[1:].split("/"))
    ):
        raise StorageError(f"{name} must be a canonical absolute POSIX path")
    candidate = Path(text)
    if not candidate.is_absolute() or candidate.as_posix() != text:
        raise StorageError(f"{name} must be a canonical absolute POSIX path")
    return candidate


def _open_absolute_directory(candidate: Path, *, create_final: bool) -> int:
    """Traverse one absolute path with openat/no-follow at every component."""

    descriptor = os.open("/", os.O_RDONLY | _OPEN_BASE | _NOFOLLOW | _DIRECTORY)
    components = candidate.parts[1:]
    try:
        for index, component in enumerate(components):
            final = index == len(components) - 1
            created = False
            if final and create_final:
                try:
                    os.mkdir(component, mode=0o700, dir_fd=descriptor)
                    created = True
                except FileExistsError:
                    pass
            child = os.open(
                component,
                os.O_RDONLY | _OPEN_BASE | _NOFOLLOW | _DIRECTORY,
                dir_fd=descriptor,
            )
            if created:
                os.fsync(descriptor)
            os.close(descriptor)
            descriptor = child
        return descriptor
    except Exception:
        os.close(descriptor)
        raise


class ArtifactStore:
    """One explicit artifact root with immutable files and locked JSONL."""

    def __init__(
        self,
        root: Path | str,
        *,
        max_artifact_bytes: int = 8 * 1024 * 1024,
        max_log_bytes: int = 64 * 1024 * 1024,
        max_log_record_bytes: int = 1024 * 1024,
        forbidden_root: Path | str | None = None,
    ) -> None:
        if not storage_primitives_available():
            raise StorageUnavailable("safe POSIX storage primitives are unavailable")
        self.max_artifact_bytes = _exact_positive(
            max_artifact_bytes, "max_artifact_bytes"
        )
        self.max_log_bytes = _exact_positive(max_log_bytes, "max_log_bytes")
        self.max_log_record_bytes = _exact_positive(
            max_log_record_bytes, "max_log_record_bytes"
        )
        if self.max_log_record_bytes > self.max_log_bytes:
            raise StorageError("log record limit cannot exceed total log limit")

        self._root_descriptor: int | None = None
        candidate = _absolute_path(root, "artifact root")
        if forbidden_root is not None:
            forbidden = _absolute_path(forbidden_root, "forbidden root")
            try:
                candidate.relative_to(forbidden)
            except ValueError:
                pass
            else:
                raise StorageError("artifact root must be outside the forbidden root")
        descriptor: int | None = None
        try:
            descriptor = _open_absolute_directory(candidate, create_final=True)
            details = os.fstat(descriptor)
        except OSError as error:
            if descriptor is not None:
                os.close(descriptor)
            raise StorageError("artifact root is unavailable") from error
        assert descriptor is not None
        if not stat.S_ISDIR(details.st_mode):
            os.close(descriptor)
            raise StorageError("artifact root must be a directory")
        self.root = candidate
        self._root_identity = (details.st_dev, details.st_ino)
        self._root_descriptor = descriptor
        try:
            verified = self._open_root()
        except Exception:
            self.close()
            raise
        os.close(verified)

    def close(self) -> None:
        descriptor = self._root_descriptor
        if descriptor is not None:
            self._root_descriptor = None
            os.close(descriptor)

    def __enter__(self) -> "ArtifactStore":
        if self._root_descriptor is None:
            raise StorageError("artifact store is closed")
        return self

    def __exit__(self, _type: Any, _value: Any, _traceback: Any) -> None:
        self.close()

    def __del__(self) -> None:  # pragma: no cover - deterministic users call close.
        try:
            self.close()
        except Exception:
            pass

    def _open_root(self) -> int:
        retained = self._root_descriptor
        if retained is None:
            raise StorageError("artifact store is closed")
        descriptor: int | None = None
        current: int | None = None
        try:
            descriptor = os.dup(retained)
            details = os.fstat(descriptor)
            current = _open_absolute_directory(self.root, create_final=False)
        except OSError as error:
            if descriptor is not None:
                os.close(descriptor)
            raise StorageError("artifact root cannot be opened safely") from error
        assert descriptor is not None and current is not None
        try:
            if (details.st_dev, details.st_ino) != self._root_identity:
                raise StorageError("artifact root identity changed")
            current_details = os.fstat(current)
            if (current_details.st_dev, current_details.st_ino) != self._root_identity:
                raise StorageError("artifact root path identity changed")
        except Exception:
            os.close(descriptor)
            raise
        finally:
            os.close(current)
        return descriptor

    @contextmanager
    def _parent(
        self,
        parts: tuple[str, ...],
        *,
        create: bool,
    ) -> Iterator[tuple[int, str]]:
        descriptor = self._open_root()
        try:
            for component in parts[:-1]:
                try:
                    child = os.open(
                        component,
                        os.O_RDONLY | _OPEN_BASE | _NOFOLLOW | _DIRECTORY,
                        dir_fd=descriptor,
                    )
                except FileNotFoundError:
                    if not create:
                        raise StorageError("artifact parent does not exist")
                    try:
                        created = False
                        try:
                            os.mkdir(component, mode=0o700, dir_fd=descriptor)
                            created = True
                        except FileExistsError:
                            # A concurrent safe writer may have won this
                            # component.  The no-follow directory open below
                            # authenticates what appeared before using it.
                            pass
                        if created:
                            os.fsync(descriptor)
                        child = os.open(
                            component,
                            os.O_RDONLY | _OPEN_BASE | _NOFOLLOW | _DIRECTORY,
                            dir_fd=descriptor,
                        )
                    except OSError as error:
                        raise StorageError(
                            "artifact parent cannot be created safely"
                        ) from error
                except OSError as error:
                    raise StorageError(
                        "artifact parent is not a safe directory"
                    ) from error
                os.close(descriptor)
                descriptor = child
            yield descriptor, parts[-1]
        finally:
            os.close(descriptor)

    @staticmethod
    def _regular_unlinked(descriptor: int) -> os.stat_result:
        details = os.fstat(descriptor)
        if not stat.S_ISREG(details.st_mode):
            raise ArtifactCorrupt("artifact is not a regular file")
        if details.st_nlink != 1:
            raise ArtifactCorrupt("artifact has an unsafe hard-link count")
        return details

    def exists(self, relative_path: str) -> bool:
        """Check one confined locator without following any path component."""

        parts = _relative_parts(relative_path)
        descriptor = self._open_root()
        try:
            for index, component in enumerate(parts):
                if index == len(parts) - 1:
                    try:
                        os.stat(component, dir_fd=descriptor, follow_symlinks=False)
                    except FileNotFoundError:
                        return False
                    except OSError as error:
                        raise StorageError(
                            "artifact existence cannot be checked safely"
                        ) from error
                    return True
                try:
                    child = os.open(
                        component,
                        os.O_RDONLY | _OPEN_BASE | _NOFOLLOW | _DIRECTORY,
                        dir_fd=descriptor,
                    )
                except FileNotFoundError:
                    return False
                except OSError as error:
                    raise StorageError(
                        "artifact parent is not a safe directory"
                    ) from error
                os.close(descriptor)
                descriptor = child
        finally:
            os.close(descriptor)
        return False

    def create_bytes(self, relative_path: str, payload: bytes) -> StoredArtifact:
        """Install immutable bytes atomically without replacing a target."""

        parts = _relative_parts(relative_path)
        if type(payload) is not bytes:
            raise StorageError("artifact payload must be bytes")
        if len(payload) > self.max_artifact_bytes:
            raise StorageError("artifact exceeds its byte limit")
        digest = hashlib.sha256(payload).hexdigest()

        with self._parent(parts, create=True) as (parent, final_name):
            temporary_name = (
                f".{final_name}.tmp-{os.getpid()}-{secrets.token_hex(12)}"
            )
            descriptor: int | None = None
            linked = False
            try:
                descriptor = os.open(
                    temporary_name,
                    os.O_WRONLY
                    | os.O_CREAT
                    | os.O_EXCL
                    | _OPEN_BASE
                    | _NOFOLLOW,
                    0o600,
                    dir_fd=parent,
                )
                _write_all(descriptor, payload)
                os.fsync(descriptor)
                os.close(descriptor)
                descriptor = None
                try:
                    os.link(
                        temporary_name,
                        final_name,
                        src_dir_fd=parent,
                        dst_dir_fd=parent,
                        follow_symlinks=False,
                    )
                except FileExistsError as error:
                    raise ArtifactExists(
                        f"create-only artifact already exists: {relative_path}"
                    ) from error
                linked = True
                os.fsync(parent)
            except ArtifactExists:
                raise
            except OSError as error:
                raise StorageError("artifact cannot be retained atomically") from error
            finally:
                if descriptor is not None:
                    os.close(descriptor)
                try:
                    os.unlink(temporary_name, dir_fd=parent)
                    os.fsync(parent)
                except FileNotFoundError:
                    pass
                except OSError as error:
                    if linked:
                        # Publication is only complete after the staging link
                        # is gone and the directory has been synced.  Roll our
                        # new target back when possible; never report success
                        # with a two-link artifact that readers must reject.
                        try:
                            os.unlink(final_name, dir_fd=parent)
                            os.fsync(parent)
                        except OSError:
                            pass
                    raise StorageError(
                        "artifact staging link cannot be removed safely"
                    ) from error

        return StoredArtifact(relative_path, digest, len(payload))

    def create_json(self, relative_path: str, value: Any) -> StoredArtifact:
        try:
            payload = canonical_json_bytes(value)
        except (TypeError, ValueError) as error:
            raise StorageError(
                "artifact is outside the canonical JSON domain"
            ) from error
        return self.create_bytes(relative_path, payload)

    def read_bytes(
        self,
        relative_path: str,
        *,
        expected_sha256: str | None = None,
    ) -> bytes:
        parts = _relative_parts(relative_path)
        if expected_sha256 is not None and (
            type(expected_sha256) is not str
            or _SHA256_RE.fullmatch(expected_sha256) is None
        ):
            raise StorageError("expected artifact digest is invalid")
        with self._parent(parts, create=False) as (parent, name):
            try:
                descriptor = os.open(
                    name,
                    os.O_RDONLY | _OPEN_BASE | _NOFOLLOW,
                    dir_fd=parent,
                )
            except OSError as error:
                raise StorageError("artifact cannot be opened safely") from error
            try:
                details = self._regular_unlinked(descriptor)
                if details.st_size > self.max_artifact_bytes:
                    raise ArtifactCorrupt("artifact exceeds its byte limit")
                chunks: list[bytes] = []
                total = 0
                while True:
                    chunk = os.read(
                        descriptor,
                        min(1024 * 1024, self.max_artifact_bytes + 1),
                    )
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > self.max_artifact_bytes:
                        raise ArtifactCorrupt("artifact exceeds its byte limit")
                    chunks.append(chunk)
            finally:
                os.close(descriptor)
        payload = b"".join(chunks)
        if (
            expected_sha256 is not None
            and hashlib.sha256(payload).hexdigest() != expected_sha256
        ):
            raise ArtifactCorrupt("artifact digest differs from its authority")
        return payload

    def read_json(
        self,
        relative_path: str,
        *,
        expected_sha256: str | None = None,
    ) -> Any:
        payload = self.read_bytes(
            relative_path, expected_sha256=expected_sha256
        )
        try:
            value = strict_loads(payload, label=relative_path)
            if canonical_json_bytes(value) != payload:
                raise ArtifactCorrupt("artifact JSON is not canonical")
        except ArtifactCorrupt:
            raise
        except (TypeError, ValueError) as error:
            raise ArtifactCorrupt("artifact is not strict JSON") from error
        return value

    @contextmanager
    def writer_lock(
        self, name: str, *, blocking: bool = False
    ) -> Iterator[None]:
        """Own one persistent advisory lock below the artifact root."""

        if _fcntl is None:
            raise StorageUnavailable("flock is unavailable")
        if type(name) is not str or _LOCK_NAME_RE.fullmatch(name) is None:
            raise StorageError("writer lock name is invalid")
        if type(blocking) is not bool:
            raise StorageError("blocking must be an exact boolean")
        parts = _relative_parts(f".locks/{name}.lock", internal=True)
        with self._parent(parts, create=True) as (parent, filename):
            descriptor: int | None = None
            try:
                descriptor = os.open(
                    filename,
                    os.O_RDWR | os.O_CREAT | _OPEN_BASE | _NOFOLLOW,
                    0o600,
                    dir_fd=parent,
                )
                self._regular_unlinked(descriptor)
            except ArtifactCorrupt:
                if descriptor is not None:
                    os.close(descriptor)
                raise
            except OSError as error:
                if descriptor is not None:
                    os.close(descriptor)
                raise StorageError("writer lock cannot be opened safely") from error
            assert descriptor is not None
            operation = _fcntl.LOCK_EX
            if not blocking:
                operation |= _fcntl.LOCK_NB
            acquired = False
            try:
                try:
                    _fcntl.flock(descriptor, operation)
                    acquired = True
                except BlockingIOError as error:
                    raise WriterLockBusy(
                        f"writer lock is already held: {name}"
                    ) from error
                except OSError as error:
                    raise StorageError(
                        "writer lock cannot be acquired safely"
                    ) from error
                yield
            finally:
                try:
                    if acquired:
                        try:
                            _fcntl.flock(descriptor, _fcntl.LOCK_UN)
                        except OSError as error:
                            raise StorageError(
                                "writer lock cannot be released safely"
                            ) from error
                finally:
                    os.close(descriptor)

    def append_jsonl(
        self,
        relative_path: str,
        value: Any,
        *,
        lock_name: str,
    ) -> AppendedRecord:
        """Append one canonical line under ``flock`` and fsync it.

        A nonempty log must end in a newline before another record is accepted;
        this makes a torn final record a fail-closed replay error rather than a
        prefix that the next writer silently extends.
        """

        parts = _relative_parts(relative_path)
        try:
            line = canonical_json_bytes(value) + b"\n"
        except (TypeError, ValueError) as error:
            raise StorageError("log record is outside canonical JSON") from error
        if len(line) > self.max_log_record_bytes:
            raise StorageError("log record exceeds its byte limit")

        with self.writer_lock(lock_name):
            with self._parent(parts, create=True) as (parent, filename):
                try:
                    descriptor = os.open(
                        filename,
                        os.O_RDWR
                        | os.O_APPEND
                        | os.O_CREAT
                        | _OPEN_BASE
                        | _NOFOLLOW,
                        0o600,
                        dir_fd=parent,
                    )
                except OSError as error:
                    raise StorageError("event log cannot be opened safely") from error
                try:
                    details = self._regular_unlinked(descriptor)
                    if details.st_size > self.max_log_bytes - len(line):
                        raise StorageError("event log exceeds its byte limit")
                    if details.st_size:
                        last = os.pread(descriptor, 1, details.st_size - 1)
                        if last != b"\n":
                            raise ArtifactCorrupt("event log has a torn final record")
                    offset = details.st_size
                    _write_all(descriptor, line)
                    os.fsync(descriptor)
                    os.fsync(parent)
                finally:
                    os.close(descriptor)
        return AppendedRecord(
            relative_path=relative_path,
            offset=offset,
            size_bytes=len(line),
            sha256=hashlib.sha256(line).hexdigest(),
        )


__all__ = [
    "AppendedRecord",
    "ArtifactCorrupt",
    "ArtifactExists",
    "ArtifactStore",
    "StorageError",
    "StorageUnavailable",
    "StoredArtifact",
    "WriterLockBusy",
    "storage_primitives_available",
]
