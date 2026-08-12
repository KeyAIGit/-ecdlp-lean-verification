"""Bounded subprocess boundary for the P04 method and validator workers.

Only trusted coordinator code constructs :class:`WorkerModules`.  Campaign or
fixture JSON selects neither a module nor an argv element.  A child receives
exactly one canonical JSON object on stdin and must return exactly one
canonical JSON object on stdout; diagnostic stderr is captured separately.

This is a resource/process boundary for the lab's reviewed worker modules, not
a general arbitrary-code sandbox.  In particular it deliberately exposes no
raw-command API.
"""

from __future__ import annotations

import hashlib
import ctypes
import os
import re
import selectors
import signal
import stat
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import Any, Mapping

from experiments.ecdlp_lab.core.canonical import (
    canonical_json_bytes,
    strict_loads,
)

try:  # ``resource`` is intentionally unavailable on native Windows.
    import resource as _resource
except ImportError:  # pragma: no cover - exercised through the patched probe.
    _resource = None


_ROLE_NAMES = frozenset({"method", "validator"})
_MODULE_RE = re.compile(
    r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+\Z"
)
_MAX_LIMIT_VALUE = 1 << 50
_READ_CHUNK = 64 * 1024
_MAX_JSON_NESTING = 64
_MAX_STAGED_FILE_BYTES = 8 * 1024 * 1024
_MAX_STAGED_ROLE_BYTES = 64 * 1024 * 1024
_SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
_PR_SET_CHILD_SUBREAPER = 36
_PR_GET_CHILD_SUBREAPER = 37
_WORKER_BOUNDARY_LOCK = threading.Lock()

try:
    _PID_NAMESPACE_INODE = os.stat("/proc/self/ns/pid").st_ino
except OSError:  # pragma: no cover - non-Linux fail-closed path.
    _PID_NAMESPACE_INODE = None

try:
    _LIBC = ctypes.CDLL(None, use_errno=True)
    _PRCTL = _LIBC.prctl
    _PRCTL.restype = ctypes.c_int
except (AttributeError, OSError):  # pragma: no cover - non-Linux fail-closed path.
    _PRCTL = None


class ProcessBoundaryError(ValueError):
    """A process request cannot safely cross the worker boundary."""


class ResourceEnforcementUnavailable(ProcessBoundaryError):
    """The requested hard address-space limit cannot be enforced."""


class ProcessTreeEnforcementUnavailable(ProcessBoundaryError):
    """The coordinator cannot own and reap the worker's complete process tree."""


class WorkerSourceDrift(ProcessBoundaryError):
    """A code-owned worker source entry differs from its pinned manifest."""


@dataclass(frozen=True, order=True)
class WorkerCodeEntry:
    """One exact source/data file staged into a role's private code tree."""

    relative_path: str
    sha256: str
    size_bytes: int

    def __post_init__(self) -> None:
        path = self.relative_path
        if (
            type(path) is not str
            or not path
            or "\x00" in path
            or "\\" in path
        ):
            raise ProcessBoundaryError("worker source path must be relative POSIX text")
        pure = PurePosixPath(path)
        parts = pure.parts
        if (
            pure.is_absolute()
            or not parts
            or any(part in {"", ".", ".."} for part in parts)
            or path != "/".join(parts)
        ):
            raise ProcessBoundaryError("worker source path is noncanonical or escapes")
        folded = tuple(part.casefold() for part in parts)
        if (
            any("private" in part for part in folded)
            or ".git" in folded
            or any(
                folded[index : index + 2] == ("experiments", "engine")
                for index in range(max(0, len(folded) - 1))
            )
        ):
            raise ProcessBoundaryError("worker source path enters a private/protected tree")
        if type(self.sha256) is not str or _SHA256_RE.fullmatch(self.sha256) is None:
            raise ProcessBoundaryError("worker source digest must be lowercase SHA-256")
        if (
            type(self.size_bytes) is not int
            or not 0 <= self.size_bytes <= _MAX_STAGED_FILE_BYTES
        ):
            raise ProcessBoundaryError("worker source size is outside its fixed bound")


@dataclass(frozen=True)
class WorkerModules:
    """Code-owned role-to-module allowlist.

    ``python_path`` is the reviewed import root.  It is not a worker cwd and is
    never taken from a campaign record.  Keeping the mapping in one immutable
    value makes it difficult for a caller to accidentally pass a fixture field
    through as a module name.
    """

    method: str
    validator: str
    python_path: Path
    method_files: tuple[WorkerCodeEntry, ...]
    validator_files: tuple[WorkerCodeEntry, ...]

    def __post_init__(self) -> None:
        for role in sorted(_ROLE_NAMES):
            module = getattr(self, role)
            if type(module) is not str or _MODULE_RE.fullmatch(module) is None:
                raise ProcessBoundaryError(
                    f"{role} worker module must be a dotted Python identifier"
                )
        raw_root = Path(self.python_path)
        try:
            if raw_root.is_symlink():
                raise ProcessBoundaryError("worker python_path cannot be a symlink")
            root = raw_root.resolve(strict=True)
        except OSError as error:
            raise ProcessBoundaryError("worker python_path is unavailable") from error
        if not root.is_dir():
            raise ProcessBoundaryError("worker python_path must be a directory")
        object.__setattr__(self, "python_path", root)
        for role in sorted(_ROLE_NAMES):
            self._validate_role_files(role, root)

    def _validate_role_files(self, role: str, root: Path | None = None) -> None:
        source_root = self.python_path if root is None else root
        entries = getattr(self, f"{role}_files")
        if type(entries) is not tuple or not entries or any(
            not isinstance(entry, WorkerCodeEntry) for entry in entries
        ):
            raise ProcessBoundaryError(
                f"{role} worker files must be a nonempty WorkerCodeEntry tuple"
            )
        paths = tuple(entry.relative_path for entry in entries)
        if paths != tuple(sorted(paths)) or len(paths) != len(set(paths)):
            raise ProcessBoundaryError(
                f"{role} worker source paths must be unique and sorted"
            )
        if sum(entry.size_bytes for entry in entries) > _MAX_STAGED_ROLE_BYTES:
            raise ProcessBoundaryError(f"{role} worker source manifest is oversized")
        module_path = self.module_for(role).replace(".", "/") + ".py"
        if module_path not in paths:
            raise ProcessBoundaryError(
                f"{role} worker module file is absent from its source manifest"
            )

        path_set = frozenset(paths)
        for relative_path in paths:
            parent = PurePosixPath(relative_path).parent
            while parent != PurePosixPath("."):
                init_relative = (parent / "__init__.py").as_posix()
                init_source = source_root.joinpath(*PurePosixPath(init_relative).parts)
                try:
                    init_exists = init_source.exists()
                    init_is_link = init_source.is_symlink()
                except OSError as error:
                    raise WorkerSourceDrift(
                        f"cannot inspect package initializer {init_relative}"
                    ) from error
                if init_is_link:
                    raise WorkerSourceDrift(
                        f"package initializer is a symlink: {init_relative}"
                    )
                if init_exists and init_relative not in path_set:
                    raise ProcessBoundaryError(
                        f"{role} worker manifest omits package initializer "
                        f"{init_relative}"
                    )
                parent = parent.parent

    def module_for(self, role: str) -> str:
        if type(role) is not str or role not in _ROLE_NAMES:
            raise ProcessBoundaryError("worker role is not allowlisted")
        return getattr(self, role)

    def files_for(self, role: str) -> tuple[WorkerCodeEntry, ...]:
        self.module_for(role)
        return getattr(self, f"{role}_files")

    @property
    def as_mapping(self) -> Mapping[str, str]:
        return MappingProxyType(
            {"method": self.method, "validator": self.validator}
        )


@dataclass(frozen=True)
class ProcessLimits:
    """Hard and deterministic limits for one worker invocation."""

    memory_bytes: int
    timeout_ns: int
    term_grace_ns: int = 250_000_000
    max_stdin_bytes: int = 256 * 1024
    max_stdout_bytes: int = 1024 * 1024
    max_stderr_bytes: int = 256 * 1024
    max_json_bytes: int = 1024 * 1024

    def __post_init__(self) -> None:
        for name in self.__dataclass_fields__:
            value = getattr(self, name)
            if type(value) is not int or not 1 <= value <= _MAX_LIMIT_VALUE:
                raise ProcessBoundaryError(
                    f"{name} must be an exact positive bounded integer"
                )
        if self.max_json_bytes > self.max_stdout_bytes:
            raise ProcessBoundaryError(
                "max_json_bytes cannot exceed max_stdout_bytes"
            )
        if self.term_grace_ns > self.timeout_ns:
            raise ProcessBoundaryError("termination grace cannot exceed timeout")


@dataclass(frozen=True)
class ProcessResult:
    """Bounded public observation of one worker process."""

    role: str
    status: str
    returncode: int | None
    output: dict[str, Any] | None
    timed_out: bool
    terminated: bool
    stdout_bytes: int
    stderr_bytes: int
    stdout_sha256: str
    stderr_sha256: str
    stderr_excerpt: str

    @property
    def passed(self) -> bool:
        return self.status == "success"


def memory_enforcement_available() -> bool:
    """Return whether P04 can install a hard ``RLIMIT_AS`` guard.

    P04 intentionally fails closed outside Linux/WSL.  Merely finding a
    similarly named limit on another platform is not enough to claim the hard
    memory enforcement required by the task contract.
    """

    return (
        sys.platform.startswith("linux")
        and os.name == "posix"
        and _resource is not None
        and hasattr(_resource, "RLIMIT_AS")
        and hasattr(_resource, "setrlimit")
    )


def process_tree_enforcement_available() -> bool:
    """Return whether Linux subreaper and procfs tracking are available."""

    return (
        sys.platform.startswith("linux")
        and os.name == "posix"
        and _PRCTL is not None
        and _PID_NAMESPACE_INODE is not None
        and Path("/proc/self/task").is_dir()
    )


def _ensure_subreaper() -> None:
    if not process_tree_enforcement_available():
        raise ProcessTreeEnforcementUnavailable(
            "Linux subreaper/procfs process-tree enforcement is unavailable"
        )
    assert _PRCTL is not None
    if _PRCTL(
        _PR_SET_CHILD_SUBREAPER,
        ctypes.c_ulong(1),
        ctypes.c_ulong(0),
        ctypes.c_ulong(0),
        ctypes.c_ulong(0),
    ) != 0:
        error = ctypes.get_errno()
        raise ProcessTreeEnforcementUnavailable(
            f"cannot enable Linux child subreaper: errno {error}"
        )
    enabled = ctypes.c_int(0)
    if _PRCTL(
        _PR_GET_CHILD_SUBREAPER,
        ctypes.byref(enabled),
        ctypes.c_ulong(0),
        ctypes.c_ulong(0),
        ctypes.c_ulong(0),
    ) != 0 or enabled.value != 1:
        error = ctypes.get_errno()
        raise ProcessTreeEnforcementUnavailable(
            f"cannot verify Linux child subreaper: errno {error}"
        )


@dataclass(frozen=True)
class _ProcessIdentity:
    pid: int
    proc_pid: int
    start_time: int


@dataclass(frozen=True)
class _ProcRecord:
    identity: _ProcessIdentity
    state: str
    parent_pid: int
    process_group: int
    session: int


def _proc_record_at(proc_pid: int) -> _ProcRecord | None:
    try:
        if (
            _PID_NAMESPACE_INODE is None
            or os.stat(f"/proc/{proc_pid}/ns/pid").st_ino
            != _PID_NAMESPACE_INODE
        ):
            return None
        raw = Path(f"/proc/{proc_pid}/stat").read_text(encoding="ascii")
        status = Path(f"/proc/{proc_pid}/status").read_text(encoding="ascii")
        closing = raw.rfind(") ")
        if closing < 0:
            return None
        fields = raw[closing + 2 :].split()
        if len(fields) < 20:
            return None
        namespace_pid = proc_pid
        for line in status.splitlines():
            if line.startswith("NSpid:"):
                values = line.split()[1:]
                if values:
                    namespace_pid = int(values[-1])
                break
        return _ProcRecord(
            identity=_ProcessIdentity(
                namespace_pid, proc_pid, int(fields[19])
            ),
            state=fields[0],
            # These stat identifiers use the procfs mount's namespace.  Map
            # the parent below when comparing with the coordinator; signals
            # always use the innermost NSpid stored in ``identity.pid``.
            parent_pid=int(fields[1]),
            process_group=int(fields[2]),
            session=int(fields[3]),
        )
    except (OSError, UnicodeError, ValueError):
        return None


def _proc_record(pid: int, *, proc_pid_hint: int | None = None) -> _ProcRecord | None:
    if proc_pid_hint is not None:
        hinted = _proc_record_at(proc_pid_hint)
        if hinted is not None and hinted.identity.pid == pid:
            return hinted
    direct = _proc_record_at(pid)
    if direct is not None and direct.identity.pid == pid:
        return direct
    try:
        candidates = tuple(Path("/proc").iterdir())
    except OSError:
        return None
    for candidate in candidates:
        if not candidate.name.isdigit():
            continue
        record = _proc_record_at(int(candidate.name))
        if record is not None and record.identity.pid == pid:
            return record
    return None


def _proc_children(pid: int) -> set[int]:
    children: set[int] = set()
    parent = _proc_record(pid)
    if parent is None:
        return children
    try:
        candidates = tuple(Path("/proc").iterdir())
    except OSError:
        return children
    for candidate in candidates:
        if not candidate.name.isdigit():
            continue
        record = _proc_record_at(int(candidate.name))
        if (
            record is not None
            and record.parent_pid == parent.identity.proc_pid
            and record.identity.pid > 0
        ):
            children.add(record.identity.pid)
    return children


def _direct_child_identities() -> frozenset[_ProcessIdentity]:
    identities: set[_ProcessIdentity] = set()
    for pid in _proc_children(os.getpid()):
        record = _proc_record(pid)
        parent = _proc_record_at(record.parent_pid) if record is not None else None
        if (
            record is not None
            and parent is not None
            and parent.identity.pid == os.getpid()
        ):
            identities.add(record.identity)
    return frozenset(identities)


class _DescendantTracker:
    """Track one serialized worker tree across setsid and double-fork."""

    def __init__(self) -> None:
        self._baseline = _direct_child_identities()
        if self._baseline:
            raise ProcessTreeEnforcementUnavailable(
                "worker boundary requires exclusive ownership of child processes"
            )
        self._tracked: dict[int, _ProcessIdentity] = {}
        self.leader_pid: int | None = None

    def bind(self, leader_pid: int) -> None:
        record = _proc_record(leader_pid)
        parent = _proc_record_at(record.parent_pid) if record is not None else None
        if (
            record is None
            or parent is None
            or parent.identity.pid != os.getpid()
        ):
            raise ProcessTreeEnforcementUnavailable(
                "spawned worker cannot be identified through procfs"
            )
        self.leader_pid = leader_pid
        self._tracked[leader_pid] = record.identity
        self.refresh()

    def _add_pid(self, pid: int) -> bool:
        record = _proc_record(pid)
        if record is None or pid == os.getpid():
            return False
        prior = self._tracked.get(pid)
        if prior is not None and prior == record.identity:
            return False
        self._tracked[pid] = record.identity
        return True

    def refresh(self) -> None:
        # Descendants that have not orphaned yet remain discoverable beneath a
        # tracked PID.  Once a worker lineage double-forks, subreaper adoption
        # makes it a new direct child distinct from the pre-spawn baseline.
        queue = list(self._tracked)
        visited: set[int] = set()
        while queue:
            parent = queue.pop()
            if parent in visited:
                continue
            visited.add(parent)
            for child in _proc_children(parent):
                if self._add_pid(child):
                    queue.append(child)
        for identity in _direct_child_identities():
            if identity not in self._baseline:
                self._tracked[identity.pid] = identity

    def records(self) -> tuple[_ProcRecord, ...]:
        self.refresh()
        records: list[_ProcRecord] = []
        for identity in tuple(self._tracked.values()):
            record = _proc_record(
                identity.pid, proc_pid_hint=identity.proc_pid
            )
            if record is not None and record.identity == identity:
                records.append(record)
        return tuple(records)

    def signal(self, signum: int) -> bool:
        sent = False
        records = self.records()
        for record in records:
            try:
                os.kill(record.identity.pid, signum)
                sent = True
            except ProcessLookupError:
                pass
            except PermissionError:
                continue
        return sent

    def reap(self) -> None:
        self.refresh()
        for identity in tuple(self._tracked.values()):
            if identity.pid == self.leader_pid:
                continue
            record = _proc_record(
                identity.pid, proc_pid_hint=identity.proc_pid
            )
            if record is None or record.identity != identity:
                continue
            try:
                os.waitpid(identity.pid, os.WNOHANG)
            except (ChildProcessError, OSError):
                pass

    def running(self) -> tuple[_ProcRecord, ...]:
        self.reap()
        return tuple(record for record in self.records() if record.state != "Z")


def _preexec_with_memory_limit(memory_bytes: int):
    if not memory_enforcement_available():
        raise ResourceEnforcementUnavailable(
            "hard address-space enforcement is unavailable"
        )

    def apply_limit() -> None:
        assert _resource is not None
        current_soft, current_hard = _resource.getrlimit(_resource.RLIMIT_AS)
        del current_soft
        effective = memory_bytes
        if current_hard != _resource.RLIM_INFINITY:
            effective = min(effective, current_hard)
        _resource.setrlimit(_resource.RLIMIT_AS, (effective, effective))
        if hasattr(_resource, "RLIMIT_CORE"):
            _resource.setrlimit(_resource.RLIMIT_CORE, (0, 0))

    return apply_limit


def _scrubbed_environment(
    *, python_path: Path, home: Path, temporary: Path
) -> dict[str, str]:
    """Build an allowlist environment without inheriting credentials."""

    python_bin = str(Path(sys.executable).resolve().parent)
    return {
        "HOME": str(home),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "PATH": python_bin + os.pathsep + os.defpath,
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "PYTHONPATH": str(python_path),
        "TEMP": str(temporary),
        "TMP": str(temporary),
        "TMPDIR": str(temporary),
        "TZ": "UTC",
    }


def _read_pinned_source(root: Path, entry: WorkerCodeEntry) -> bytes:
    source = root.joinpath(*PurePosixPath(entry.relative_path).parts)
    current = root
    try:
        for component in PurePosixPath(entry.relative_path).parts:
            current = current / component
            if current.is_symlink():
                raise WorkerSourceDrift(
                    f"worker source contains a symlink: {entry.relative_path}"
                )
        descriptor = os.open(
            source,
            os.O_RDONLY
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0),
        )
    except WorkerSourceDrift:
        raise
    except OSError as error:
        raise WorkerSourceDrift(
            f"worker source cannot be opened: {entry.relative_path}"
        ) from error
    try:
        details = os.fstat(descriptor)
        if not stat.S_ISREG(details.st_mode) or details.st_size != entry.size_bytes:
            raise WorkerSourceDrift(
                f"worker source size/type drifted: {entry.relative_path}"
            )
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(
                descriptor,
                min(1024 * 1024, entry.size_bytes + 1 - total),
            )
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > entry.size_bytes:
                raise WorkerSourceDrift(
                    f"worker source grew while read: {entry.relative_path}"
                )
    finally:
        os.close(descriptor)
    payload = b"".join(chunks)
    if (
        len(payload) != entry.size_bytes
        or hashlib.sha256(payload).hexdigest() != entry.sha256
    ):
        raise WorkerSourceDrift(
            f"worker source digest drifted: {entry.relative_path}"
        )
    return payload


def _stage_role_files(
    worker_modules: WorkerModules, role: str, code_root: Path
) -> None:
    worker_modules._validate_role_files(role)
    for entry in worker_modules.files_for(role):
        payload = _read_pinned_source(worker_modules.python_path, entry)
        destination = code_root.joinpath(
            *PurePosixPath(entry.relative_path).parts
        )
        destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        descriptor = os.open(
            destination,
            os.O_WRONLY
            | os.O_CREAT
            | os.O_EXCL
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0),
            0o400,
        )
        try:
            view = memoryview(payload)
            while view:
                written = os.write(descriptor, view)
                if written <= 0:
                    raise WorkerSourceDrift(
                        f"cannot stage worker source: {entry.relative_path}"
                    )
                view = view[written:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        staged = destination.read_bytes()
        if (
            len(staged) != entry.size_bytes
            or hashlib.sha256(staged).hexdigest() != entry.sha256
        ):
            raise WorkerSourceDrift(
                f"staged worker source failed verification: {entry.relative_path}"
            )


def _json_nesting_within_limit(payload: bytes) -> bool:
    depth = 0
    in_string = False
    escaped = False
    for value in payload:
        if in_string:
            if escaped:
                escaped = False
            elif value == 0x5C:  # backslash
                escaped = True
            elif value == 0x22:  # quote
                in_string = False
            continue
        if value == 0x22:
            in_string = True
        elif value in (0x5B, 0x7B):  # [ {
            depth += 1
            if depth > _MAX_JSON_NESTING:
                return False
        elif value in (0x5D, 0x7D):  # ] }
            depth -= 1
            if depth < 0:
                return False
    return depth == 0 and not in_string and not escaped


def _group_exists(process_group: int) -> bool:
    try:
        os.killpg(process_group, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _signal_group(process: subprocess.Popen[bytes], signum: int) -> bool:
    """Signal the child's new session, falling back to its leader."""

    sent = False
    try:
        os.killpg(process.pid, signum)
        sent = True
    except ProcessLookupError:
        pass
    except (AttributeError, PermissionError, OSError):
        if process.poll() is None:
            try:
                process.send_signal(signum)
                sent = True
            except ProcessLookupError:
                pass
    return sent


def _terminate_tree(
    process: subprocess.Popen[bytes],
    tracker: _DescendantTracker,
    *,
    grace_ns: int,
) -> tuple[bool, bool]:
    """TERM then KILL every tracked descendant, including escaped sessions."""

    terminated = _signal_group(process, signal.SIGTERM)
    terminated = tracker.signal(signal.SIGTERM) or terminated
    deadline = time.monotonic_ns() + grace_ns
    while time.monotonic_ns() < deadline:
        process.poll()
        tracker.reap()
        if process.poll() is not None and not tracker.running():
            break
        tracker.signal(signal.SIGTERM)
        time.sleep(0.01)
    terminated = _signal_group(process, signal.SIGKILL) or terminated
    terminated = tracker.signal(signal.SIGKILL) or terminated
    try:
        process.wait(timeout=0.5)
    except subprocess.TimeoutExpired:
        _signal_group(process, signal.SIGKILL)
        tracker.signal(signal.SIGKILL)

    kill_deadline = time.monotonic_ns() + 1_000_000_000
    while time.monotonic_ns() < kill_deadline:
        process.poll()
        tracker.reap()
        running = tracker.running()
        if process.poll() is not None and not running:
            return terminated, True
        _signal_group(process, signal.SIGKILL)
        tracker.signal(signal.SIGKILL)
        time.sleep(0.01)
    return terminated, process.poll() is not None and not tracker.running()


def _kill_orphaned_tree(
    process: subprocess.Popen[bytes], tracker: _DescendantTracker
) -> tuple[bool, bool]:
    """Remove descendants that escaped pipes, groups, or their original parent."""

    process.poll()
    if tracker.running() or _group_exists(process.pid):
        return _terminate_tree(process, tracker, grace_ns=25_000_000)
    return False, True


@dataclass
class _Capture:
    stdout: bytearray
    stderr: bytearray
    stdout_hash: Any
    stderr_hash: Any
    stdout_total: int = 0
    stderr_total: int = 0
    overflow: bool = False

    @classmethod
    def empty(cls) -> "_Capture":
        return cls(bytearray(), bytearray(), hashlib.sha256(), hashlib.sha256())

    def add(self, name: str, chunk: bytes, limit: int) -> None:
        target = self.stdout if name == "stdout" else self.stderr
        digest = self.stdout_hash if name == "stdout" else self.stderr_hash
        digest.update(chunk)
        if name == "stdout":
            self.stdout_total += len(chunk)
        else:
            self.stderr_total += len(chunk)
        remaining = max(0, limit - len(target))
        target.extend(chunk[:remaining])
        if len(chunk) > remaining:
            self.overflow = True


def _capture_process(
    process: subprocess.Popen[bytes],
    limits: ProcessLimits,
    tracker: _DescendantTracker,
) -> tuple[_Capture, bool, bool, bool]:
    """Read both output streams without allowing unbounded buffering."""

    assert process.stdout is not None and process.stderr is not None
    capture = _Capture.empty()
    selector = selectors.DefaultSelector()
    for name, stream in (("stdout", process.stdout), ("stderr", process.stderr)):
        os.set_blocking(stream.fileno(), False)
        selector.register(stream, selectors.EVENT_READ, data=name)

    execution_deadline = time.monotonic_ns() + limits.timeout_ns
    drain_deadline: int | None = None
    timed_out = False
    terminated = False
    tree_clean = True
    try:
        while selector.get_map():
            now = time.monotonic_ns()
            if drain_deadline is None and now >= execution_deadline:
                timed_out = True
                was_terminated, tree_clean = _terminate_tree(
                    process, tracker, grace_ns=limits.term_grace_ns
                )
                terminated = was_terminated or terminated
                drain_deadline = time.monotonic_ns() + 1_000_000_000
            active_deadline = (
                drain_deadline
                if drain_deadline is not None
                else execution_deadline
            )
            remaining_ns = active_deadline - time.monotonic_ns()
            if remaining_ns <= 0:
                for key in tuple(selector.get_map().values()):
                    selector.unregister(key.fileobj)
                    key.fileobj.close()
                break
            timeout = max(0.0, min(0.05, remaining_ns / 1_000_000_000))
            events = selector.select(timeout)
            if not events and process.poll() is not None:
                # One final nonblocking pass observes EOF on both pipes.
                events = [
                    (key, selectors.EVENT_READ)
                    for key in tuple(selector.get_map().values())
                ]
            for key, _ in events:
                name = key.data
                try:
                    chunk = os.read(key.fileobj.fileno(), _READ_CHUNK)
                except BlockingIOError:
                    continue
                if not chunk:
                    selector.unregister(key.fileobj)
                    key.fileobj.close()
                    continue
                limit = (
                    limits.max_stdout_bytes
                    if name == "stdout"
                    else limits.max_stderr_bytes
                )
                capture.add(name, chunk, limit)
            if capture.overflow and drain_deadline is None:
                was_terminated, tree_clean = _terminate_tree(
                    process, tracker, grace_ns=limits.term_grace_ns
                )
                terminated = was_terminated or terminated
                drain_deadline = time.monotonic_ns() + 1_000_000_000
            if (
                drain_deadline is not None
                and time.monotonic_ns() >= drain_deadline
            ):
                # A killed descendant maliciously retaining a pipe must not
                # make the coordinator wait forever.
                for key in tuple(selector.get_map().values()):
                    selector.unregister(key.fileobj)
                    key.fileobj.close()
                break
    finally:
        selector.close()

    try:
        process.wait(timeout=0.25)
    except subprocess.TimeoutExpired:
        was_terminated, tree_clean = _terminate_tree(
            process, tracker, grace_ns=limits.term_grace_ns
        )
        terminated = was_terminated or terminated
    orphan_terminated, orphan_clean = _kill_orphaned_tree(process, tracker)
    terminated = orphan_terminated or terminated
    tree_clean = tree_clean and orphan_clean
    return capture, timed_out, terminated, tree_clean


def _result(
    *,
    role: str,
    status: str,
    returncode: int | None,
    output: dict[str, Any] | None,
    capture: _Capture,
    timed_out: bool,
    terminated: bool,
) -> ProcessResult:
    return ProcessResult(
        role=role,
        status=status,
        returncode=returncode,
        output=output,
        timed_out=timed_out,
        terminated=terminated,
        stdout_bytes=capture.stdout_total,
        stderr_bytes=capture.stderr_total,
        stdout_sha256=capture.stdout_hash.hexdigest(),
        stderr_sha256=capture.stderr_hash.hexdigest(),
        stderr_excerpt=bytes(capture.stderr).decode("utf-8", errors="replace"),
    )


def _run_worker_serial(
    role: str,
    payload: Mapping[str, Any],
    *,
    worker_modules: WorkerModules,
    limits: ProcessLimits,
    scratch_root: Path | str,
) -> ProcessResult:
    """Execute one allowlisted worker under deterministic process limits.

    No part of ``payload`` influences the executable, module, argv, cwd, or
    environment.  Unsupported hard-memory enforcement raises before spawn.
    """

    if not isinstance(worker_modules, WorkerModules):
        raise ProcessBoundaryError("worker_modules must be WorkerModules")
    if not isinstance(limits, ProcessLimits):
        raise ProcessBoundaryError("limits must be ProcessLimits")
    module = worker_modules.module_for(role)
    if not isinstance(payload, Mapping):
        raise ProcessBoundaryError("worker payload must be a mapping")
    try:
        stdin_bytes = canonical_json_bytes(dict(payload))
    except (MemoryError, RecursionError, TypeError, ValueError) as error:
        raise ProcessBoundaryError("worker payload is not canonical JSON") from error
    if len(stdin_bytes) > limits.max_stdin_bytes:
        raise ProcessBoundaryError("worker stdin exceeds its byte limit")
    preexec = _preexec_with_memory_limit(limits.memory_bytes)
    _ensure_subreaper()

    scratch = Path(scratch_root)
    try:
        if scratch.is_symlink():
            raise ProcessBoundaryError("scratch_root cannot be a symlink")
        scratch.mkdir(parents=True, exist_ok=True, mode=0o700)
        scratch = scratch.resolve(strict=True)
    except OSError as error:
        raise ProcessBoundaryError("scratch_root is unavailable") from error
    if not scratch.is_dir():
        raise ProcessBoundaryError("scratch_root must be a directory")

    capture = _Capture.empty()
    command = [sys.executable, "-B", "-m", module]
    with tempfile.TemporaryDirectory(prefix=f"{role}-", dir=scratch) as raw_work:
        work = Path(raw_work)
        home = work / "home"
        temporary = work / "tmp"
        code_root = work / "code"
        home.mkdir(mode=0o700)
        temporary.mkdir(mode=0o700)
        code_root.mkdir(mode=0o700)
        _stage_role_files(worker_modules, role, code_root)
        stdin_path = work / "stdin.json"
        descriptor = os.open(
            stdin_path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
            0o600,
        )
        try:
            view = memoryview(stdin_bytes)
            while view:
                written = os.write(descriptor, view)
                if written <= 0:
                    raise ProcessBoundaryError("cannot stage canonical stdin")
                view = view[written:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)

        tracker = _DescendantTracker()
        try:
            with stdin_path.open("rb") as stdin_handle:
                process = subprocess.Popen(
                    command,
                    cwd=work,
                    env=_scrubbed_environment(
                        python_path=code_root,
                        home=home,
                        temporary=temporary,
                    ),
                    stdin=stdin_handle,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=False,
                    start_new_session=True,
                    close_fds=True,
                    preexec_fn=preexec,
                )
        except (OSError, subprocess.SubprocessError):
            return _result(
                role=role,
                status="spawn_error",
                returncode=None,
                output=None,
                capture=capture,
                timed_out=False,
                terminated=False,
            )

        try:
            tracker.bind(process.pid)
        except ProcessTreeEnforcementUnavailable:
            _signal_group(process, signal.SIGKILL)
            try:
                process.wait(timeout=1.0)
            except subprocess.TimeoutExpired:
                pass
            for stream in (process.stdout, process.stderr):
                if stream is not None:
                    stream.close()
            raise

        capture, timed_out, terminated, tree_clean = _capture_process(
            process, limits, tracker
        )

    if not tree_clean:
        return _result(
            role=role,
            status="tree_cleanup_failed",
            returncode=process.returncode,
            output=None,
            capture=capture,
            timed_out=timed_out,
            terminated=terminated,
        )
    if timed_out:
        return _result(
            role=role,
            status="timeout",
            returncode=process.returncode,
            output=None,
            capture=capture,
            timed_out=True,
            terminated=terminated,
        )
    if capture.overflow:
        return _result(
            role=role,
            status="output_limit",
            returncode=process.returncode,
            output=None,
            capture=capture,
            timed_out=False,
            terminated=terminated,
        )
    if terminated:
        # A nominally successful leader is not allowed to leave a detached
        # descendant behind.  The boundary removes that process group, but
        # must not accept the leader's JSON after having done so.
        return _result(
            role=role,
            status="orphan_process",
            returncode=process.returncode,
            output=None,
            capture=capture,
            timed_out=False,
            terminated=True,
        )
    if process.returncode != 0:
        return _result(
            role=role,
            status="worker_error",
            returncode=process.returncode,
            output=None,
            capture=capture,
            timed_out=False,
            terminated=terminated,
        )

    raw_stdout = bytes(capture.stdout)
    if len(raw_stdout) > limits.max_json_bytes:
        status = "output_limit"
        output = None
    elif not _json_nesting_within_limit(raw_stdout):
        status = "invalid_output"
        output = None
    else:
        try:
            parsed = strict_loads(raw_stdout, label=f"{role} worker stdout")
            if not isinstance(parsed, dict):
                raise ValueError("worker stdout must be an object")
            if canonical_json_bytes(parsed) != raw_stdout:
                raise ValueError("worker stdout is not canonical JSON")
        except (MemoryError, RecursionError, TypeError, ValueError):
            status = "invalid_output"
            output = None
        else:
            status = "success"
            output = parsed
    return _result(
        role=role,
        status=status,
        returncode=process.returncode,
        output=output,
        capture=capture,
        timed_out=False,
        terminated=terminated,
    )


def run_worker(
    role: str,
    payload: Mapping[str, Any],
    *,
    worker_modules: WorkerModules,
    limits: ProcessLimits,
    scratch_root: Path | str,
) -> ProcessResult:
    """Serialize one exclusively owned, manifest-staged worker invocation.

    ``RLIMIT_AS`` is a per-process address-space guard.  This boundary is for
    reviewed workers and makes no cgroup-wide aggregate-memory claim.
    """

    if not _WORKER_BOUNDARY_LOCK.acquire(blocking=False):
        raise ProcessTreeEnforcementUnavailable(
            "another worker boundary is already active in this coordinator"
        )
    try:
        return _run_worker_serial(
            role,
            payload,
            worker_modules=worker_modules,
            limits=limits,
            scratch_root=scratch_root,
        )
    finally:
        _WORKER_BOUNDARY_LOCK.release()


__all__ = [
    "ProcessBoundaryError",
    "ProcessLimits",
    "ProcessResult",
    "ProcessTreeEnforcementUnavailable",
    "ResourceEnforcementUnavailable",
    "WorkerCodeEntry",
    "WorkerModules",
    "WorkerSourceDrift",
    "memory_enforcement_available",
    "process_tree_enforcement_available",
    "run_worker",
]
