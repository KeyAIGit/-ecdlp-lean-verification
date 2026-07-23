#!/usr/bin/env python3
"""Build a deterministic, read-only snapshot of a pinned Lean repository.

This is deliberately narrower than a project importer. It inventories source,
build, trust, and dependency signals without editing the inspected repository or
inventing claims, tasks, decisions, or verifier results.
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable
from functools import lru_cache
from pathlib import Path, PurePosixPath
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONTRACT = ROOT / "repo" / "PORTABILITY_REHEARSAL.json"
GENERATOR_ID = "keyai-lean-portability"
GENERATOR_VERSION = "1.0"

DECL_RE = re.compile(
    r"^\s*(?:@\[[^\]]*\]\s*)?"
    r"(?P<mods>(?:(?:public|private|protected|noncomputable|scoped|local|unsafe|partial)\s+)*)"
    r"(?P<kind>theorem|lemma|def|abbrev|instance|opaque|structure|class|inductive|"
    r"axiom|constant)\s+"
    r"(?P<name>«[^»]+»|[^\s(:\[{:=]+)"
)
ANON_INSTANCE_RE = re.compile(
    r"^\s*(?:@\[[^\]]*\]\s*)?"
    r"(?:(?:public|private|noncomputable|scoped|local|unsafe)\s+)*instance\s*:"
)
CONTEXT_MODIFIERS = r"(?P<mods>(?:(?:public|private|local|scoped)\s+)*)"
ATTRIBUTE_PREFIX = r"(?:@\[[^\]]*\]\s*)?"
NAMESPACE_RE = re.compile(
    rf"^\s*{ATTRIBUTE_PREFIX}{CONTEXT_MODIFIERS}"
    r"namespace\s+(?P<name>[^\s]+)\s*$"
)
SECTION_RE = re.compile(
    rf"^\s*{ATTRIBUTE_PREFIX}{CONTEXT_MODIFIERS}"
    r"section(?:\s+(?P<name>[^\s]+))?\s*$"
)
MUTUAL_RE = re.compile(
    rf"^\s*{ATTRIBUTE_PREFIX}{CONTEXT_MODIFIERS}mutual\s*$"
)
END_RE = re.compile(r"^\s*end(?:\s+[^\s]+)?\s*$")
IMPORT_RE = re.compile(r"^\s*(?:(?:public|private|meta)\s+)*import\s+(.+?)\s*$")
SORRY_RE = re.compile(r"(?<![A-Za-z0-9_'])sorry(?![A-Za-z0-9_'])")
ADMIT_RE = re.compile(r"(?<![A-Za-z0-9_'])admit(?![A-Za-z0-9_'])")

BUILD_FILES = {
    "lakefile.lean",
    "lakefile.toml",
    "lake-manifest.json",
    "lean-toolchain",
    "pyproject.toml",
    "requirements.txt",
}
LICENSE_NAMES = {
    "license",
    "license.md",
    "license.txt",
    "copying",
    "copying.md",
    "copying.txt",
}
DOCUMENT_SUFFIXES = {".md", ".rst", ".txt", ".adoc", ".tex"}
CI_PREFIXES = (".github/workflows/", ".gitlab-ci", "azure-pipelines")


class PortabilityError(RuntimeError):
    """Raised when a source checkout violates the rehearsal contract."""


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        .encode("utf-8")
    )


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalized_source_sha256(path: Path) -> str:
    try:
        text = path.read_bytes().decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise PortabilityError(f"cannot hash UTF-8 source {path}: {exc}") from exc
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return sha256_bytes(normalized.encode("utf-8"))


def normalized_rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def is_safe_relative(value: str) -> bool:
    path = PurePosixPath(value)
    return (
        bool(value)
        and value == value.strip()
        and not any(ord(char) < 32 for char in value)
        and "\\" not in value
        and ":" not in value
        and not path.is_absolute()
        and ".." not in path.parts
    )


def strip_comments_and_strings(text: str) -> str:
    """Replace Lean comments and strings with spaces while preserving newlines."""
    out: list[str] = []
    i = 0
    block_depth = 0
    in_string = False
    escaped = False
    while i < len(text):
        pair = text[i : i + 2]
        char = text[i]
        if block_depth:
            if pair == "/-":
                block_depth += 1
                out.extend((" ", " "))
                i += 2
                continue
            if pair == "-/":
                block_depth -= 1
                out.extend((" ", " "))
                i += 2
                continue
            out.append("\n" if char == "\n" else " ")
            i += 1
            continue
        if in_string:
            out.append("\n" if char == "\n" else " ")
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            i += 1
            continue
        if pair == "/-":
            block_depth = 1
            out.extend((" ", " "))
            i += 2
            continue
        if pair == "--":
            while i < len(text) and text[i] != "\n":
                out.append(" ")
                i += 1
            continue
        if char == '"':
            in_string = True
            out.append(" ")
            i += 1
            continue
        out.append(char)
        i += 1
    return "".join(out)


def parse_imports(clean_text: str) -> list[str]:
    imports: list[str] = []
    for line in clean_text.splitlines():
        match = IMPORT_RE.match(line)
        if not match:
            continue
        imports.extend(
            token
            for token in match.group(1).split()
            if re.fullmatch(r"[A-Za-z0-9_'.]+", token)
        )
    return sorted(set(imports))


def parse_declarations(clean_text: str, rel: str) -> tuple[list[dict], int]:
    contexts: list[tuple[str, str | None, str | None]] = []
    declarations: list[dict] = []
    anonymous_instances = 0
    module_mode = any(
        line.strip() == "module" for line in clean_text.splitlines()
    )
    for line_number, line in enumerate(clean_text.splitlines(), 1):
        namespace = NAMESPACE_RE.match(line)
        if namespace:
            modifiers = namespace.group("mods").split()
            context_visibility = (
                "private"
                if "private" in modifiers or "local" in modifiers
                else "public" if "public" in modifiers else None
            )
            contexts.append(
                ("namespace", namespace.group("name"), context_visibility)
            )
            continue
        section = SECTION_RE.match(line)
        if section:
            modifiers = section.group("mods").split()
            context_visibility = (
                "private"
                if "private" in modifiers or "local" in modifiers
                else "public" if "public" in modifiers else None
            )
            contexts.append(("section", None, context_visibility))
            continue
        mutual = MUTUAL_RE.match(line)
        if mutual:
            modifiers = mutual.group("mods").split()
            context_visibility = (
                "private"
                if "private" in modifiers or "local" in modifiers
                else "public" if "public" in modifiers else None
            )
            contexts.append(("mutual", None, context_visibility))
            continue
        if END_RE.match(line):
            if contexts:
                contexts.pop()
            continue
        match = DECL_RE.match(line)
        if match:
            modifiers = match.group("mods").split()
            namespace_name = ".".join(
                value
                for kind, value, _ in contexts
                if kind == "namespace" and value
            )
            inherited_visibility = next(
                (
                    visibility
                    for _, _, visibility in reversed(contexts)
                    if visibility is not None
                ),
                None,
            )
            name = match.group("name")
            if name.startswith("«") and name.endswith("»"):
                name = name[1:-1]
            if "private" in modifiers or "local" in modifiers:
                visibility = "private"
            elif "public" in modifiers:
                visibility = "public"
            elif inherited_visibility == "private":
                visibility = "private"
            elif inherited_visibility == "public":
                visibility = "public"
            elif module_mode:
                visibility = "module_private"
            else:
                visibility = "public"
            declarations.append(
                {
                    "qualified_name": (
                        f"{namespace_name}.{name}" if namespace_name else name
                    ),
                    "name": name,
                    "namespace": namespace_name,
                    "kind": match.group("kind"),
                    "visibility": visibility,
                    "module_mode": module_mode,
                    "modifiers": modifiers,
                    "file": rel,
                    "line": line_number,
                }
            )
            continue
        if ANON_INSTANCE_RE.match(line):
            anonymous_instances += 1
    return declarations, anonymous_instances


def module_for_path(rel: str, module_roots: list[dict]) -> str | None:
    path = PurePosixPath(rel)
    matches: list[tuple[int, str]] = []
    for item in module_roots:
        root = PurePosixPath(item["path"])
        try:
            inside = path.relative_to(root)
        except ValueError:
            continue
        if inside.suffix != ".lean":
            continue
        stem = inside.with_suffix("").as_posix().replace("/", ".")
        prefix = item.get("module_prefix", "").strip(".")
        module = ".".join(part for part in (prefix, stem) if part)
        matches.append((len(root.parts), module))
    if not matches:
        return None
    max_depth = max(depth for depth, _ in matches)
    most_specific = {
        module for depth, module in matches if depth == max_depth
    }
    if len(most_specific) != 1:
        raise PortabilityError(
            f"ambiguous module roots for {rel}: {sorted(most_specific)}"
        )
    return next(iter(most_specific))


def matches_any(path: str, patterns: Iterable[str]) -> bool:
    return any(
        fnmatch.fnmatchcase(path, pattern)
        or PurePosixPath(path).match(pattern)
        for pattern in patterns
    )


def classify_path(rel: str, module: str | None, adapter: dict) -> str:
    lower = rel.lower()
    name = PurePosixPath(lower).name
    if matches_any(rel, adapter.get("explicit_exclusions", [])):
        return "explicitly_excluded"
    if lower.endswith(".lean"):
        return "lean_source" if module else "lean_out_of_scope"
    if name in BUILD_FILES:
        return "build_configuration"
    if name in LICENSE_NAMES or name.startswith("license."):
        return "license"
    if lower.startswith(CI_PREFIXES):
        return "ci"
    if PurePosixPath(lower).suffix in DOCUMENT_SUFFIXES:
        return "documentation"
    if lower.startswith((".git/", ".lake/")):
        return "repository_internal"
    return "other"


@lru_cache(maxsize=1)
def find_git() -> str:
    git = shutil.which("git")
    if git:
        return git
    runtime_root = Path.home() / ".cache" / "codex-runtimes"
    candidate = next(runtime_root.rglob("git.exe"), None)
    if candidate:
        return str(candidate)
    raise PortabilityError("git executable not found")


def git_environment() -> dict[str, str]:
    inherited = {
        key: os.environ[key]
        for key in (
            "COMSPEC",
            "NUMBER_OF_PROCESSORS",
            "PATHEXT",
            "PROCESSOR_ARCHITECTURE",
            "SYSTEMROOT",
            "WINDIR",
        )
        if key in os.environ
    }
    path_parts = [str(Path(find_git()).parent)]
    system_root = inherited.get("SYSTEMROOT") or inherited.get("WINDIR")
    if system_root:
        path_parts.append(str(Path(system_root) / "System32"))
    inherited.update(
        {
            "GIT_ATTR_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": "NUL" if os.name == "nt" else "/dev/null",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_OPTIONAL_LOCKS": "0",
            "GIT_PAGER": "cat",
            "GIT_TERMINAL_PROMPT": "0",
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "PAGER": "cat",
            "PATH": os.pathsep.join(path_parts),
        }
    )
    return inherited


def git_output(source: Path, *args: str) -> str:
    result = subprocess.run(
        [find_git(), *args],
        cwd=source,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        env=git_environment(),
    )
    if result.returncode:
        raise PortabilityError(
            f"git {' '.join(args)} failed in {source}: {result.stderr.strip()}"
        )
    return result.stdout


def git_tracked_files(source: Path) -> list[str]:
    output = git_output(source, "ls-files", "-z")
    paths = [item for item in output.split("\0") if item]
    unsafe = [path for path in paths if not is_safe_relative(path)]
    if unsafe:
        raise PortabilityError(f"unsafe tracked paths: {unsafe[:5]}")
    return sorted(paths)


def git_tree_entries(source: Path, revision: str) -> dict[str, dict[str, str]]:
    result = subprocess.run(
        [find_git(), "ls-tree", "-rz", "--full-tree", revision],
        cwd=source,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=git_environment(),
    )
    if result.returncode:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise PortabilityError(f"cannot inspect committed tree {revision}: {message}")
    entries: dict[str, dict[str, str]] = {}
    for raw_entry in result.stdout.split(b"\0"):
        if not raw_entry:
            continue
        try:
            header, raw_path = raw_entry.split(b"\t", 1)
            mode, object_type, object_id = header.decode("ascii").split()
            rel = raw_path.decode("utf-8")
        except (UnicodeDecodeError, ValueError) as exc:
            raise PortabilityError("invalid Git tree entry") from exc
        if not is_safe_relative(rel):
            raise PortabilityError(f"unsafe committed path: {rel!r}")
        entries[rel] = {
            "mode": mode,
            "object_type": object_type,
            "object_id": object_id,
        }
    return dict(sorted(entries.items()))


def verify_pinned_checkout(source: Path, expected_revision: str) -> list[str]:
    actual = git_output(source, "rev-parse", "HEAD").strip()
    if actual != expected_revision:
        raise PortabilityError(
            f"source revision mismatch: expected {expected_revision}, got {actual}"
        )
    dirty = git_output(source, "status", "--porcelain=v1", "--untracked-files=all")
    if dirty.strip():
        raise PortabilityError("source checkout must be clean and read-only")
    return git_tracked_files(source)


def git_blob_bytes(source: Path, revision: str, rel: str) -> bytes:
    result = subprocess.run(
        [find_git(), "cat-file", "blob", f"{revision}:{rel}"],
        cwd=source,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=git_environment(),
    )
    if result.returncode:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise PortabilityError(f"cannot read committed blob {rel}: {message}")
    return result.stdout


def git_blob_map(
    source: Path,
    revision: str,
    paths: list[str],
) -> dict[str, bytes]:
    request = b"".join(
        f"{revision}:{rel}\n".encode("utf-8") for rel in paths
    )
    result = subprocess.run(
        [find_git(), "cat-file", "--batch"],
        cwd=source,
        check=False,
        input=request,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=git_environment(),
    )
    if result.returncode:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise PortabilityError(f"cannot batch-read committed blobs: {message}")
    blobs: dict[str, bytes] = {}
    offset = 0
    for rel in paths:
        header_end = result.stdout.find(b"\n", offset)
        if header_end < 0:
            raise PortabilityError(f"truncated Git batch header for {rel}")
        header = result.stdout[offset:header_end].decode(
            "ascii",
            errors="replace",
        )
        fields = header.split()
        if len(fields) != 3 or fields[1] != "blob":
            raise PortabilityError(f"unexpected Git batch header for {rel}: {header}")
        try:
            size = int(fields[2])
        except ValueError as exc:
            raise PortabilityError(f"invalid Git blob size for {rel}") from exc
        start = header_end + 1
        end = start + size
        if end >= len(result.stdout) or result.stdout[end : end + 1] != b"\n":
            raise PortabilityError(f"truncated Git batch body for {rel}")
        blobs[rel] = result.stdout[start:end]
        offset = end + 1
    if offset != len(result.stdout):
        raise PortabilityError("unexpected trailing data from Git batch")
    return blobs


def safe_worktree_bytes(source: Path, rel: str) -> bytes:
    path = source / Path(rel)
    if path.is_symlink():
        raise PortabilityError(f"refusing to follow a tracked symlink: {rel}")
    try:
        path.resolve(strict=True).relative_to(source.resolve(strict=True))
    except ValueError as exc:
        raise PortabilityError(f"tracked path escapes the source checkout: {rel}") from exc
    if not path.is_file():
        raise PortabilityError(f"tracked path is not a regular file: {rel}")
    return path.read_bytes()


def validate_adapter(adapter: dict) -> None:
    roots = adapter.get("module_roots")
    if not isinstance(roots, list) or not roots:
        raise PortabilityError("adapter.module_roots must be a non-empty list")
    root_paths: list[str] = []
    for item in roots:
        if not isinstance(item, dict) or not is_safe_relative(item.get("path", "")):
            raise PortabilityError("each module root needs a safe relative path")
        root_paths.append(item["path"])
        prefix = item.get("module_prefix", "")
        if not isinstance(prefix, str) or "/" in prefix or "\\" in prefix:
            raise PortabilityError("module_prefix must be a dotted module prefix")
    if len(root_paths) != len(set(root_paths)):
        raise PortabilityError("adapter.module_roots must use unique paths")
    for key in ("explicit_exclusions", "entrypoints", "owned_module_prefixes"):
        values = adapter.get(key, [])
        if not isinstance(values, list) or not all(
            isinstance(value, str) and value for value in values
        ):
            raise PortabilityError(f"adapter.{key} must be a list of strings")
    if not adapter.get("entrypoints"):
        raise PortabilityError("adapter.entrypoints must not be empty")
    if not adapter.get("owned_module_prefixes"):
        raise PortabilityError("adapter.owned_module_prefixes must not be empty")


def build_snapshot(
    source: Path,
    contract: dict,
    revision: str,
    tracked_paths: list[str],
    file_loader: Callable[[str], bytes] | None = None,
    git_entries: dict[str, dict[str, str]] | None = None,
) -> dict:
    selected = contract["selected_source"]
    adapter = selected["adapter"]
    validate_adapter(adapter)
    read_bytes = file_loader or (lambda rel: safe_worktree_bytes(source, rel))
    tracked_set = set(tracked_paths)
    license_file = selected["license_file"]
    toolchain_file = selected.get("toolchain_file", "lean-toolchain")
    for required_path, label in (
        (license_file, "license"),
        (toolchain_file, "toolchain"),
    ):
        if required_path not in tracked_set:
            raise PortabilityError(f"selected {label} file is not tracked: {required_path}")
    actual_license_sha = sha256_bytes(read_bytes(license_file))
    if actual_license_sha != selected["license_sha256"]:
        raise PortabilityError(
            "license hash mismatch: "
            f"expected {selected['license_sha256']}, got {actual_license_sha}"
        )
    try:
        actual_toolchain = read_bytes(toolchain_file).decode("utf-8").strip()
    except UnicodeDecodeError as exc:
        raise PortabilityError("toolchain file is not UTF-8") from exc
    if actual_toolchain != selected["lean_toolchain"]:
        raise PortabilityError(
            "lean toolchain mismatch: "
            f"expected {selected['lean_toolchain']!r}, got {actual_toolchain!r}"
        )
    records: list[dict] = []
    modules: dict[str, dict] = {}
    declarations: list[dict] = []
    anonymous_instances = 0
    sorry_count = 0
    admit_count = 0

    for rel in sorted(tracked_paths):
        entry = (git_entries or {}).get(
            rel,
            {
                "mode": "100644",
                "object_type": "blob",
                "object_id": "",
            },
        )
        mode = entry["mode"]
        object_type = entry["object_type"]
        if object_type == "commit" or mode == "160000":
            records.append(
                {
                    "path": rel,
                    "classification": "gitlink",
                    "bytes": 0,
                    "sha256": None,
                    "git_mode": mode,
                    "git_object_type": object_type,
                    "git_object_id": entry["object_id"],
                }
            )
            continue
        if object_type != "blob" or mode not in {"100644", "100755", "120000"}:
            raise PortabilityError(
                f"unsupported Git object at {rel}: mode={mode}, type={object_type}"
            )
        data = read_bytes(rel)
        module = module_for_path(rel, adapter["module_roots"])
        classification = (
            "symlink"
            if mode == "120000"
            else classify_path(rel, module, adapter)
        )
        record = {
            "path": rel,
            "classification": classification,
            "bytes": len(data),
            "sha256": sha256_bytes(data),
            "git_mode": mode,
            "git_object_type": object_type,
            "git_object_id": entry["object_id"] or None,
        }
        if classification == "lean_source":
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise PortabilityError(f"Lean source is not UTF-8: {rel}") from exc
            clean = strip_comments_and_strings(text)
            imports = parse_imports(clean)
            file_declarations, file_anonymous = parse_declarations(clean, rel)
            file_sorry = len(SORRY_RE.findall(clean))
            file_admit = len(ADMIT_RE.findall(clean))
            record.update(
                {
                    "module": module,
                    "imports": imports,
                    "declaration_count": len(file_declarations),
                    "anonymous_instance_count": file_anonymous,
                    "sorry_token_count": file_sorry,
                    "admit_token_count": file_admit,
                }
            )
            if module in modules:
                raise PortabilityError(
                    f"module collision: {module} maps to both "
                    f"{modules[module]['file']} and {rel}"
                )
            modules[module] = {
                "module": module,
                "file": rel,
                "imports": imports,
            }
            declarations.extend(file_declarations)
            anonymous_instances += file_anonymous
            sorry_count += file_sorry
            admit_count += file_admit
        records.append(record)

    module_names = set(modules)
    missing_entrypoints = sorted(
        entrypoint
        for entrypoint in adapter["entrypoints"]
        if entrypoint not in module_names
    )
    if missing_entrypoints:
        raise PortabilityError(
            f"configured entrypoints are missing: {', '.join(missing_entrypoints)}"
        )
    owned_prefixes = tuple(adapter["owned_module_prefixes"])
    unresolved_local: list[dict] = []
    for module in modules.values():
        module["internal_imports"] = sorted(
            dependency for dependency in module["imports"] if dependency in module_names
        )
        module["external_imports"] = sorted(
            dependency for dependency in module["imports"] if dependency not in module_names
        )
        for dependency in module["external_imports"]:
            if any(
                dependency == prefix or dependency.startswith(f"{prefix}.")
                for prefix in owned_prefixes
            ):
                unresolved_local.append(
                    {"module": module["module"], "missing_import": dependency}
                )
    if unresolved_local:
        rendered = ", ".join(
            f"{item['module']} -> {item['missing_import']}"
            for item in unresolved_local[:10]
        )
        raise PortabilityError(f"unresolved local imports: {rendered}")

    classifications: dict[str, int] = {}
    for record in records:
        label = record["classification"]
        classifications[label] = classifications.get(label, 0) + 1
    axiom_declarations = [
        item["qualified_name"]
        for item in declarations
        if item["kind"] in {"axiom", "constant"}
    ]
    public_declarations = sum(
        item["visibility"] == "public" for item in declarations
    )
    unsupported_lean = [
        item["path"]
        for item in records
        if item["classification"] == "lean_out_of_scope"
        or (
            item["path"].lower().endswith(".lean")
            and item["classification"] in {"symlink", "gitlink"}
        )
    ]

    snapshot = {
        "schema_version": "1.0",
        "rehearsal_id": contract["id"],
        "task_id": contract["task_id"],
        "generator": {
            "id": GENERATOR_ID,
            "version": GENERATOR_VERSION,
            "path": "scripts/lean_portability.py",
        },
        "evidence_class": "internal_technical_rehearsal",
        "external_evidence": False,
        "unlocks_task_012": False,
        "source": {
            "repository": selected["repository"],
            "commit_sha": revision,
            "tree_sha": selected["tree_sha"],
            "license_spdx": selected["license_spdx"],
            "license_file": selected["license_file"],
            "license_sha256": actual_license_sha,
            "toolchain_file": toolchain_file,
            "lean_toolchain": selected["lean_toolchain"],
        },
        "adapter": adapter,
        "summary": {
            "tracked_files": len(records),
            "classified_files": len(records),
            "classification_counts": dict(sorted(classifications.items())),
            "lean_modules": len(modules),
            "source_declarations": len(declarations),
            "public_source_declarations": public_declarations,
            "anonymous_instances": anonymous_instances,
            "sorry_tokens": sorry_count,
            "admit_tokens": admit_count,
            "axiom_or_constant_declarations": len(axiom_declarations),
            "unsupported_lean_files": len(unsupported_lean),
        },
        "trust_boundary": {
            "inventory": (
                "File hashes, imports, declaration heads, and trust tokens are "
                "source-level observations."
            ),
            "build": (
                "A successful pinned baseline build is separate evidence and is "
                "not inferred by this snapshot."
            ),
            "proof": (
                "Only the inspected project's Lean kernel build can establish "
                "that declarations elaborate; this snapshot does not certify them."
            ),
            "product": (
                "This internal rehearsal is not user, retention, workflow-value, "
                "or willingness-to-pay evidence."
            ),
        },
        "limitations": [
            "Declaration extraction records source headings, not the compiled Lean environment.",
            "Axiom and constant headings are flagged but their transitive use is not inferred.",
            "Imports are file-level source observations and may include conditional build behavior not represented here.",
            "Files outside configured module roots remain visible as lean_out_of_scope.",
        ],
        "entrypoints": selected["adapter"].get("entrypoints", []),
        "unsupported_lean_files": unsupported_lean,
        "axiom_or_constant_declarations": sorted(axiom_declarations),
        "modules": [modules[name] for name in sorted(modules)],
        "declarations": sorted(
            declarations,
            key=lambda item: (item["file"], item["line"], item["qualified_name"]),
        ),
        "files": records,
    }
    snapshot["content_manifest_sha256"] = sha256_bytes(canonical_json_bytes(records))
    snapshot["snapshot_sha256"] = sha256_bytes(canonical_json_bytes(snapshot))
    return snapshot


def load_contract(path: Path) -> dict:
    try:
        contract = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise PortabilityError(f"cannot read contract {path}: {exc}") from exc
    if contract.get("schema_version") != "1.0":
        raise PortabilityError("portability contract schema_version must be 1.0")
    selected = contract.get("selected_source")
    if not isinstance(selected, dict):
        raise PortabilityError("portability contract has no selected_source")
    required = {
        "repository",
        "commit_sha",
        "tree_sha",
        "license_spdx",
        "license_file",
        "license_sha256",
        "toolchain_file",
        "lean_toolchain",
        "adapter",
    }
    missing = sorted(required - set(selected))
    if missing:
        raise PortabilityError(f"selected_source is missing: {', '.join(missing)}")
    revision = selected.get("commit_sha", "")
    if re.fullmatch(r"[0-9a-f]{40}", revision) is None:
        raise PortabilityError("selected_source.commit_sha must be a full Git SHA")
    if re.fullmatch(r"[0-9a-f]{40}", selected.get("tree_sha", "")) is None:
        raise PortabilityError("selected_source.tree_sha must be a full Git tree SHA")
    if re.fullmatch(r"[0-9a-f]{64}", selected.get("license_sha256", "")) is None:
        raise PortabilityError("selected_source.license_sha256 must be a SHA-256")
    return contract


def resolve_output(contract: dict) -> Path:
    value = contract.get("artifacts", {}).get("snapshot")
    if not isinstance(value, str) or not is_safe_relative(value):
        raise PortabilityError("snapshot output must be a safe repository-relative path")
    expected = (
        PurePosixPath("rehearsals")
        / contract["id"].lower()
        / "snapshot.json"
    )
    if PurePosixPath(value) != expected:
        raise PortabilityError(f"snapshot output must be exactly {expected.as_posix()}")
    output = ROOT / value
    cursor = ROOT
    for part in output.relative_to(ROOT).parts:
        cursor = cursor / part
        if cursor.exists() and cursor.is_symlink():
            raise PortabilityError(
                f"snapshot output traverses a symlink: {cursor}"
            )
    try:
        output.resolve().relative_to(ROOT.resolve())
    except ValueError as exc:
        raise PortabilityError("snapshot output escapes the KeyAI repository") from exc
    return output


def write_json_atomic(output: Path, value: dict) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(
        prefix=f".{output.name}.",
        suffix=".tmp",
        dir=output.parent,
    )
    temporary_path = Path(temporary)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(canonical_json_bytes(value).decode("utf-8"))
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, output)
    finally:
        temporary_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="clean checkout of the pinned source")
    parser.add_argument(
        "--contract",
        default=str(DEFAULT_CONTRACT),
        help="canonical portability rehearsal contract",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if the committed snapshot differs from a fresh source inspection",
    )
    args = parser.parse_args()

    try:
        source = Path(args.source).resolve(strict=True)
        if not source.is_dir():
            raise PortabilityError(f"source is not a directory: {source}")
        contract = load_contract(Path(args.contract))
        revision = contract["selected_source"]["commit_sha"]
        tracked = verify_pinned_checkout(source, revision)
        tree_sha = git_output(source, "rev-parse", f"{revision}^{{tree}}").strip()
        if tree_sha != contract["selected_source"]["tree_sha"]:
            raise PortabilityError(
                "source tree mismatch: expected "
                f"{contract['selected_source']['tree_sha']}, got {tree_sha}"
            )
        entries = git_tree_entries(source, revision)
        if set(entries) != set(tracked):
            raise PortabilityError(
                "committed tree paths differ from the checked-out tracked paths"
            )
        blob_paths = [
            path
            for path, entry in entries.items()
            if entry["object_type"] == "blob"
        ]
        blobs = git_blob_map(source, revision, blob_paths)
        snapshot = build_snapshot(
            source,
            contract,
            revision,
            tracked,
            file_loader=blobs.__getitem__,
            git_entries=entries,
        )
        if verify_pinned_checkout(source, revision) != tracked:
            raise PortabilityError("tracked source paths changed during inspection")
        output = resolve_output(contract)
        if args.check:
            if not output.is_file():
                raise PortabilityError(f"committed snapshot is missing: {output}")
            if json.loads(output.read_text(encoding="utf-8")) != snapshot:
                raise PortabilityError(f"committed snapshot is stale: {output}")
            print(
                "portability snapshot check OK: "
                f"{snapshot['summary']['tracked_files']} tracked files, "
                f"{snapshot['summary']['lean_modules']} Lean modules"
            )
            return 0
        if output.exists():
            try:
                existing = json.loads(output.read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                raise PortabilityError(
                    f"refusing to overwrite an unreadable snapshot: {output}"
                ) from exc
            if (
                existing.get("rehearsal_id") != contract["id"]
                or existing.get("generator", {}).get("id") != GENERATOR_ID
            ):
                raise PortabilityError(
                    f"refusing to overwrite an unowned artifact: {output}"
                )
        write_json_atomic(output, snapshot)
        print(
            f"wrote {output.relative_to(ROOT)}: "
            f"{snapshot['summary']['tracked_files']} tracked files, "
            f"{snapshot['summary']['lean_modules']} Lean modules, "
            f"digest {snapshot['snapshot_sha256']}"
        )
        return 0
    except (OSError, PortabilityError, ValueError) as exc:
        print(f"portability snapshot FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
