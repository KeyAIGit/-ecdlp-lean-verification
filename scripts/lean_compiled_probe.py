#!/usr/bin/env python3
"""Probe a built Lean environment without changing the inspected project."""
from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path, PurePosixPath

from lean_portability import (
    GENERATOR_ID as SNAPSHOT_GENERATOR_ID,
    PortabilityError,
    canonical_json_bytes,
    find_git,
    git_environment,
    is_safe_relative,
    normalized_source_sha256,
    sha256_bytes,
)

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONTRACT = ROOT / "repo" / "PORTABILITY_REHEARSAL.json"
GENERATOR_ID = "keyai-lean-compiled-probe"
GENERATOR_VERSION = "1.0"
PROBE_PREFIX = "KEYAI_PROBE\t"
AXIOM_PREFIX = "KEYAI_AXIOM\t"
MODULE_PREFIX = "KEYAI_MODULE\t"
MODULE_NAME_RE = re.compile(r"[A-Za-z0-9_'.]+")


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise PortabilityError(f"cannot read JSON {path}: {exc}") from exc


def module_closure(modules: list[dict], entrypoints: list[str]) -> set[str]:
    by_name = {item["module"]: item for item in modules}
    missing = sorted(set(entrypoints) - set(by_name))
    if missing:
        raise PortabilityError(
            f"compiled entrypoints are absent from snapshot: {', '.join(missing)}"
        )
    closure: set[str] = set()
    pending = list(reversed(entrypoints))
    while pending:
        name = pending.pop()
        if name in closure:
            continue
        closure.add(name)
        pending.extend(
            dependency
            for dependency in reversed(by_name[name].get("internal_imports", []))
            if dependency not in closure
        )
    return closure


def select_targets(snapshot: dict, entrypoints: list[str]) -> tuple[set[str], list[dict]]:
    closure = module_closure(snapshot["modules"], entrypoints)
    return closure, source_targets_for_modules(snapshot, closure)


def source_targets_for_modules(snapshot: dict, modules: set[str]) -> list[dict]:
    files = {
        item["file"]
        for item in snapshot["modules"]
        if item["module"] in modules
    }
    targets = [
        {
            "name": item["qualified_name"],
            "kind": item["kind"],
            "file": item["file"],
        }
        for item in snapshot["declarations"]
        if item["visibility"] == "public" and item["file"] in files
    ]
    names = [item["name"] for item in targets]
    duplicates = sorted(
        name for name in set(names) if names.count(name) > 1
    )
    if duplicates:
        raise PortabilityError(
            f"duplicate public declaration names in source inventory: {duplicates[:10]}"
        )
    return sorted(targets, key=lambda item: item["name"])


def lean_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def render_probe(entrypoints: list[str], owned_modules: list[str]) -> str:
    for module in [*entrypoints, *owned_modules]:
        if MODULE_NAME_RE.fullmatch(module) is None:
            raise PortabilityError(f"invalid compiled entrypoint: {module!r}")
    imports = "\n".join(f"import {module}" for module in entrypoints)
    module_rows = ",\n".join(
        f"    {lean_string(module)}" for module in owned_modules
    )
    return f"""{imports}
import Lean.Elab.Command
import Lean.Util.CollectAxioms

open Lean Elab Command

run_cmd do
  let allowedModules : Array String := #[
{module_rows}
  ]
  let env ← getEnv
  for moduleName in env.header.moduleNames do
    if allowedModules.contains moduleName.toString then
      liftIO <| IO.println s!"KEYAI_MODULE\\t{{moduleName}}"
  for (name, _) in env.constants do
    if let some moduleIdx := env.getModuleIdxFor? name then
      let moduleName := env.header.moduleNames[moduleIdx.toNat]!
      if allowedModules.contains moduleName.toString && !isPrivateName name then
        let axioms ← collectAxioms name
        let rendered := String.intercalate "," (axioms.toList.map toString)
        liftIO <| IO.println s!"KEYAI_PROBE\\tFOUND\\t{{name}}\\t{{moduleName}}\\t{{isPrivateName name}}\\t{{rendered}}"
        for axiomName in axioms do
          let kind :=
            match env.find? axiomName with
            | some (.axiomInfo _) => "axiom"
            | some _ => "non_axiom"
            | none => "missing"
          let axiomModule :=
            match env.getModuleIdxFor? axiomName with
            | some idx => env.header.moduleNames[idx.toNat]!.toString
            | none => ""
          liftIO <| IO.println s!"KEYAI_AXIOM\\t{{axiomName}}\\t{{kind}}\\t{{axiomModule}}\\t{{isPrivateName axiomName}}"
"""


def parse_probe_output(
    output: str,
    allowed_modules: set[str],
) -> tuple[list[dict], dict[str, dict], set[str]]:
    observed: dict[str, dict] = {}
    axiom_provenance: dict[str, dict] = {}
    observed_modules: set[str] = set()
    for line in output.splitlines():
        if line.startswith(MODULE_PREFIX):
            module = line.removeprefix(MODULE_PREFIX)
            if module not in allowed_modules:
                raise PortabilityError(
                    f"compiled environment returned unowned module: {module}"
                )
            observed_modules.add(module)
            continue
        if line.startswith(PROBE_PREFIX):
            parts = line.split("\t", 5)
            if len(parts) != 6:
                raise PortabilityError(f"malformed compiled probe line: {line!r}")
            _, status, name, module, private_text, rendered_axioms = parts
            if status != "FOUND":
                raise PortabilityError(
                    f"compiled environment returned invalid status for {name}: {status}"
                )
            if private_text != "false":
                raise PortabilityError(
                    f"compiled environment returned a private constant: {name}"
                )
            if module not in allowed_modules:
                raise PortabilityError(
                    f"compiled environment returned out-of-closure module: {module}"
                )
            if name in observed:
                raise PortabilityError(
                    f"compiled environment returned duplicate name: {name}"
                )
            observed[name] = {
                "name": name,
                "module": module,
                "visibility": "public",
                "status": "found",
                "axioms": (
                    sorted(set(rendered_axioms.split(",")))
                    if rendered_axioms
                    else []
                ),
            }
            continue
        if line.startswith(AXIOM_PREFIX):
            parts = line.split("\t", 4)
            if len(parts) != 5:
                raise PortabilityError(f"malformed axiom provenance line: {line!r}")
            _, name, kind, module, private_text = parts
            if kind not in {"axiom", "non_axiom", "missing"}:
                raise PortabilityError(f"invalid axiom provenance kind: {line!r}")
            if private_text not in {"true", "false"}:
                raise PortabilityError(f"invalid axiom private marker: {line!r}")
            record = {
                "name": name,
                "kind": kind,
                "module": module or None,
                "private": private_text == "true",
            }
            previous = axiom_provenance.get(name)
            if previous is not None and previous != record:
                raise PortabilityError(
                    f"conflicting axiom provenance for {name}"
                )
            axiom_provenance[name] = record
    if not observed:
        raise PortabilityError("compiled probe returned no public constants")
    if not observed_modules:
        raise PortabilityError("compiled probe returned no owned modules")
    used_axioms = {
        axiom for record in observed.values() for axiom in record["axioms"]
    }
    missing_provenance = sorted(used_axioms - set(axiom_provenance))
    if missing_provenance:
        raise PortabilityError(
            "compiled probe omitted axiom provenance: "
            + ", ".join(missing_provenance[:10])
        )
    return (
        [observed[name] for name in sorted(observed)],
        {name: axiom_provenance[name] for name in sorted(axiom_provenance)},
        observed_modules,
    )


def classify_axioms(
    records: list[dict],
    allowed_axioms: list[str],
    allowed_axiom_provenance: dict[str, dict],
    forbidden_axioms: list[str],
    accepted_groups: list[dict] | None = None,
    axiom_provenance: dict[str, dict] | None = None,
    compiled_modules: set[str] | None = None,
) -> dict:
    all_axioms = sorted(
        {
            axiom
            for record in records
            for axiom in record["axioms"]
        }
    )
    all_axiom_set = set(all_axioms)
    allowed = set(allowed_axioms)
    if set(allowed_axiom_provenance) != allowed:
        raise PortabilityError(
            "allowed axiom provenance must cover exactly the allowed axiom names"
        )
    forbidden = set(forbidden_axioms)
    invalid_allowed_provenance: list[dict] = []
    accepted_by_group: list[dict] = []
    accepted_axioms: set[str] = set()
    missing_accepted_axioms: list[str] = []
    invalid_accepted_provenance: list[dict] = []
    provenance = axiom_provenance or {}
    closure = compiled_modules or set()
    for name in sorted(all_axiom_set & allowed):
        item = provenance.get(name)
        expected = allowed_axiom_provenance[name]
        reasons: list[str] = []
        if item is None:
            reasons.append("missing_provenance")
        else:
            if item.get("kind") != expected.get("kind"):
                reasons.append("unexpected_kind")
            if item.get("module") != expected.get("module"):
                reasons.append("unexpected_module")
            if item.get("private") is not expected.get("private"):
                reasons.append("unexpected_privacy")
        if reasons:
            invalid_allowed_provenance.append(
                {"axiom": name, "reasons": reasons}
            )
    for group in accepted_groups or []:
        names = group.get("axioms", [])
        if (
            not isinstance(names, list)
            or not names
            or not all(isinstance(name, str) and name for name in names)
        ):
            raise PortabilityError(f"invalid accepted axiom group: {group!r}")
        expected = set(names)
        missing_accepted_axioms.extend(sorted(expected - all_axiom_set))
        observed = sorted(expected & all_axiom_set)
        failures: list[dict] = []
        for name in observed:
            item = provenance.get(name)
            reasons: list[str] = []
            if item is None:
                reasons.append("missing_provenance")
            else:
                if item.get("kind") != "axiom":
                    reasons.append("not_axiom_info")
                if item.get("private") is not True:
                    reasons.append("not_private")
                if item.get("module") not in closure:
                    reasons.append("module_outside_compiled_closure")
            if reasons:
                failures.append({"axiom": name, "reasons": reasons})
            else:
                accepted_axioms.add(name)
        if failures:
            invalid_accepted_provenance.extend(failures)
        if observed:
            accepted_by_group.append(
                {
                    "id": group["id"],
                    "trust_class": group["trust_class"],
                    "axioms": observed,
                }
            )
    return {
        "all": all_axioms,
        "allowed": sorted(all_axiom_set & allowed),
        "invalid_allowed_provenance": invalid_allowed_provenance,
        "accepted_by_group": accepted_by_group,
        "forbidden": sorted(all_axiom_set & forbidden),
        "unexpected": sorted(
            all_axiom_set - allowed - forbidden - accepted_axioms
        ),
        "missing_accepted_axioms": sorted(set(missing_accepted_axioms)),
        "invalid_accepted_provenance": sorted(
            invalid_accepted_provenance,
            key=lambda item: item["axiom"],
        ),
    }


def group_axiom_sets(records: list[dict]) -> list[dict]:
    groups: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for record in records:
        if record["status"] == "found":
            groups[tuple(record["axioms"])].append(record["name"])
    return [
        {
            "axioms": list(axioms),
            "declarations": sorted(names),
        }
        for axioms, names in sorted(groups.items())
    ]


def git_text(source: Path, *args: str) -> str:
    result = subprocess.run(
        [find_git(), *args],
        cwd=source,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        env=git_environment(),
    )
    if result.returncode:
        raise PortabilityError(
            f"git {' '.join(args)} failed: {result.stderr.strip()}"
        )
    return result.stdout


def workspace_changes(source: Path, allowed: list[str]) -> list[str]:
    status = git_text(
        source,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    )
    changes: list[str] = []
    for line in status.splitlines():
        if len(line) < 4 or line[2] != " ":
            raise PortabilityError(f"unsupported Git status record: {line!r}")
        path = line[3:]
        if " -> " in path or not is_safe_relative(path):
            raise PortabilityError(f"unsafe build-workspace change: {line!r}")
        changes.append(path)
    unexpected = sorted(set(changes) - set(allowed))
    if unexpected:
        raise PortabilityError(
            f"unexpected build-workspace changes: {', '.join(unexpected)}"
        )
    return sorted(changes)


def find_lake() -> str:
    lake = shutil.which("lake")
    if lake:
        return lake
    candidate = Path.home() / ".elan" / "bin" / (
        "lake.exe" if os.name == "nt" else "lake"
    )
    if candidate.is_file():
        return str(candidate)
    raise PortabilityError("lake executable not found")


def command_output(command: list[str], cwd: Path, env: dict[str, str]) -> str:
    result = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        env=env,
    )
    if result.returncode:
        detail = (result.stderr or result.stdout).strip()
        raise PortabilityError(
            f"{Path(command[0]).name} command failed ({result.returncode}): {detail}"
        )
    return result.stdout.rstrip("\r\n")


def sanitized_probe_environment(
    lake: str,
    sandbox_root: Path,
    lean_threads: str,
) -> tuple[dict[str, str], dict]:
    inherited_keys = [
        key
        for key in (
            "COMSPEC",
            "NUMBER_OF_PROCESSORS",
            "PATHEXT",
            "PROCESSOR_ARCHITECTURE",
            "SYSTEMROOT",
            "WINDIR",
        )
        if key in os.environ
    ]
    elan_home_inherited = bool(os.environ.get("ELAN_HOME"))
    if elan_home_inherited:
        inherited_keys.append("ELAN_HOME")
    env = {key: os.environ[key] for key in inherited_keys}
    home = sandbox_root / "home"
    temp = sandbox_root / "tmp"
    appdata = sandbox_root / "appdata"
    local_appdata = sandbox_root / "local-appdata"
    for path in (home, temp, appdata, local_appdata):
        path.mkdir(parents=True, exist_ok=True)
    lake_parent = str(Path(lake).parent)
    git_parent = str(Path(find_git()).parent)
    system_root = env.get("SYSTEMROOT") or env.get("WINDIR")
    path_parts = [lake_parent, git_parent]
    if system_root:
        path_parts.append(str(Path(system_root) / "System32"))
    elan_home = os.environ.get("ELAN_HOME")
    if not elan_home:
        elan_home = str(Path(lake).parent.parent)
    env.update(
        {
            "APPDATA": str(appdata),
            "ELAN_HOME": elan_home,
            "GIT_CONFIG_GLOBAL": "NUL" if os.name == "nt" else "/dev/null",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_OPTIONAL_LOCKS": "0",
            "GIT_TERMINAL_PROMPT": "0",
            "HOME": str(home),
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "LEAN_NUM_THREADS": lean_threads,
            "LOCALAPPDATA": str(local_appdata),
            "PATH": os.pathsep.join(path_parts),
            "TEMP": str(temp),
            "TMP": str(temp),
            "USERPROFILE": str(home),
        }
    )
    profile = {
        "environment_policy": "fixed_allowlist",
        "inherited_environment_keys": sorted(inherited_keys),
        "secret_like_environment_keys_inherited": [],
        "elan_home_source": (
            "parent_environment"
            if elan_home_inherited
            else "derived_from_lake_launcher"
        ),
        "lake_discovery": "host_path_or_elan_fallback",
        "lake_launcher_sha256": sha256_bytes(Path(lake).read_bytes()),
        "compiled_probe_launcher": "project_lake_env",
        "compiled_probe_output_authentication": (
            "not_independent_of_project_launcher"
        ),
        "isolated_home_and_temp": True,
        "git_optional_locks": False,
        "network_isolation": "not_os_enforced",
        "filesystem_isolation": "not_os_enforced",
        "source_workspace": "disposable_checkout",
    }
    return env, profile


def compiled_artifact_manifest(project_root: Path, modules: set[str]) -> dict:
    records: list[dict] = []
    build_root = project_root / ".lake" / "build" / "lib" / "lean"
    for module in sorted(modules):
        path = build_root.joinpath(*module.split(".")).with_suffix(".olean")
        try:
            path.resolve(strict=True).relative_to(project_root.resolve(strict=True))
        except (OSError, ValueError) as exc:
            raise PortabilityError(
                f"compiled olean is missing or escapes the project: {module}"
            ) from exc
        data = path.read_bytes()
        records.append(
            {
                "module": module,
                "path": path.relative_to(project_root).as_posix(),
                "bytes": len(data),
                "sha256": sha256_bytes(data),
            }
        )
    return {
        "module_oleans": len(records),
        "manifest_sha256": sha256_bytes(canonical_json_bytes(records)),
        "records": records,
    }


def ensure_owned_output(path: Path) -> None:
    root = ROOT.resolve(strict=True)
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise PortabilityError("compiled probe output escapes the repository") from exc
    cursor = ROOT
    for part in path.relative_to(ROOT).parts:
        cursor = cursor / part
        if cursor.exists() and cursor.is_symlink():
            raise PortabilityError(
                f"compiled probe output traverses a symlink: {cursor}"
            )
    resolved_parent = path.parent.resolve(strict=False)
    try:
        resolved_parent.relative_to(root)
    except ValueError as exc:
        raise PortabilityError("compiled probe output parent escapes repository") from exc


def artifact_path(contract: dict, key: str, filename: str) -> Path:
    value = contract.get("artifacts", {}).get(key)
    expected = (
        PurePosixPath("rehearsals")
        / contract["id"].lower()
        / filename
    )
    if (
        not isinstance(value, str)
        or not is_safe_relative(value)
        or PurePosixPath(value) != expected
    ):
        raise PortabilityError(
            f"{key} artifact must be exactly {expected.as_posix()}"
        )
    output = ROOT / value
    ensure_owned_output(output)
    return output


def write_json_atomic(output: Path, value: dict) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    ensure_owned_output(output)
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


def verify_snapshot(snapshot: dict, contract: dict) -> None:
    digest = snapshot.get("snapshot_sha256")
    unsigned = dict(snapshot)
    unsigned.pop("snapshot_sha256", None)
    if digest != sha256_bytes(canonical_json_bytes(unsigned)):
        raise PortabilityError("source snapshot digest is invalid")
    if snapshot.get("rehearsal_id") != contract["id"]:
        raise PortabilityError("source snapshot belongs to another rehearsal")
    if snapshot.get("generator", {}).get("id") != SNAPSHOT_GENERATOR_ID:
        raise PortabilityError("source snapshot has an unexpected generator")
    selected = contract["selected_source"]
    if (
        snapshot.get("source", {}).get("repository") != selected["repository"]
        or snapshot.get("source", {}).get("commit_sha") != selected["commit_sha"]
        or snapshot.get("source", {}).get("tree_sha") != selected["tree_sha"]
    ):
        raise PortabilityError("source snapshot does not match selected source")


def build_probe(source: Path, contract: dict, snapshot: dict) -> dict:
    selected = contract["selected_source"]
    baseline_adapter = selected["baseline_adapter"]
    revision = git_text(source, "rev-parse", "HEAD").strip()
    if revision != selected["commit_sha"]:
        raise PortabilityError(
            f"build workspace revision mismatch: expected {selected['commit_sha']}, "
            f"got {revision}"
        )
    tree_sha = git_text(source, "rev-parse", "HEAD^{tree}").strip()
    if tree_sha != selected["tree_sha"]:
        raise PortabilityError(
            f"build workspace tree mismatch: expected {selected['tree_sha']}, "
            f"got {tree_sha}"
        )
    changes_before = workspace_changes(
        source,
        baseline_adapter["allowed_workspace_changes"],
    )
    project_root_value = baseline_adapter["project_root"]
    if not is_safe_relative(project_root_value):
        raise PortabilityError("baseline project_root must be a safe relative path")
    project_root = (source / project_root_value).resolve(strict=True)
    try:
        project_root.relative_to(source.resolve(strict=True))
    except ValueError as exc:
        raise PortabilityError("baseline project_root escapes source") from exc
    if not project_root.is_dir():
        raise PortabilityError("baseline project_root is not a directory")

    entrypoints = baseline_adapter["compiled_entrypoints"]
    lexical_closure, lexical_targets = select_targets(snapshot, entrypoints)
    if not lexical_targets:
        raise PortabilityError("compiled probe selected no public declarations")
    owned_modules = {item["module"] for item in snapshot["modules"]}
    generated = render_probe(entrypoints, sorted(owned_modules))

    lake = find_lake()
    lean_threads = str(baseline_adapter["lean_num_threads"])
    with tempfile.TemporaryDirectory(prefix="keyai-lean-probe-") as tmp:
        sandbox_root = Path(tmp)
        env, execution_profile = sanitized_probe_environment(
            lake,
            sandbox_root,
            lean_threads,
        )
        probe_path = sandbox_root / "KeyAICompiledProbe.lean"
        probe_path.write_text(generated, encoding="utf-8", newline="\n")
        lake_version = command_output([lake, "--version"], project_root, env)
        lean_version = command_output(
            [lake, "env", "lean", "--version"],
            project_root,
            env,
        )
        output = command_output(
            [lake, "env", "lean", str(probe_path)],
            project_root,
            env,
        )
    if git_text(source, "rev-parse", "HEAD").strip() != revision:
        raise PortabilityError("build workspace revision changed during compiled probe")
    changes_after = workspace_changes(
        source,
        baseline_adapter["allowed_workspace_changes"],
    )
    if changes_after != changes_before:
        raise PortabilityError("build workspace changed during compiled probe")
    records, axiom_provenance, compiled_modules = parse_probe_output(
        output,
        owned_modules,
    )
    missing_entrypoint_modules = sorted(set(entrypoints) - compiled_modules)
    if missing_entrypoint_modules:
        raise PortabilityError(
            "compiled environment omitted entrypoint modules: "
            + ", ".join(missing_entrypoint_modules)
        )
    targets = source_targets_for_modules(snapshot, compiled_modules)
    build_manifest = compiled_artifact_manifest(project_root, compiled_modules)
    compiled_names = {record["name"] for record in records}
    source_target_names = {target["name"] for target in targets}
    missing = sorted(source_target_names - compiled_names)
    policy = contract["compiled_probe_policy"]
    axiom_classes = classify_axioms(
        records,
        policy["allowed_axioms"],
        policy["allowed_axiom_provenance"],
        policy["forbidden_axioms"],
        policy.get("accepted_axiom_groups", []),
        axiom_provenance,
        compiled_modules,
    )
    policy_pass = (
        not missing
        and not axiom_classes["forbidden"]
        and not axiom_classes["unexpected"]
        and not axiom_classes["invalid_allowed_provenance"]
        and not axiom_classes["missing_accepted_axioms"]
        and not axiom_classes["invalid_accepted_provenance"]
    )
    result = {
        "schema_version": "1.0",
        "rehearsal_id": contract["id"],
        "task_id": contract["task_id"],
        "generator": {
            "id": GENERATOR_ID,
            "version": GENERATOR_VERSION,
            "path": "scripts/lean_compiled_probe.py",
            "sha256": normalized_source_sha256(Path(__file__)),
        },
        "evidence_class": "internal_technical_rehearsal",
        "external_evidence": False,
        "unlocks_task_012": False,
        "source": {
            "repository": selected["repository"],
            "commit_sha": selected["commit_sha"],
            "tree_sha": selected["tree_sha"],
            "snapshot_sha256": snapshot["snapshot_sha256"],
            "project_root": project_root_value,
            "compiled_entrypoints": entrypoints,
            "allowed_workspace_changes": baseline_adapter[
                "allowed_workspace_changes"
            ],
            "observed_workspace_changes": changes_after,
            "compiled_modules": sorted(compiled_modules),
            "lexical_closure_modules": sorted(lexical_closure),
            "closure_difference": {
                "compiled_only": sorted(compiled_modules - lexical_closure),
                "lexical_only": sorted(lexical_closure - compiled_modules),
            },
            "compiled_artifact_manifest": build_manifest,
        },
        "environment": {
            "platform": f"{platform.system().lower()}-{platform.machine().lower()}",
            "lean_num_threads": int(lean_threads),
            "lean_version": lean_version,
            "lake_version": lake_version,
            "execution_profile": execution_profile,
        },
        "coverage": {
            "snapshot_modules": len(snapshot["modules"]),
            "compiled_closure_modules": len(compiled_modules),
            "lexical_closure_modules": len(lexical_closure),
            "snapshot_public_declarations": snapshot["summary"][
                "public_source_declarations"
            ],
            "source_public_declarations_in_compiled_closure": len(targets),
            "resolved_source_public_declarations": len(targets) - len(missing),
            "compiled_public_constants": len(records),
            "probed_public_declarations": len(records),
            "found_public_declarations": len(records),
            "missing_public_declarations": len(missing),
        },
        "trust_policy": {
            "allowed_axioms": policy["allowed_axioms"],
            "allowed_axiom_provenance": policy["allowed_axiom_provenance"],
            "forbidden_axioms": policy["forbidden_axioms"],
            "accepted_axiom_groups": policy.get(
                "accepted_axiom_groups",
                [],
            ),
            "unexpected_axioms_fail": True,
        },
        "trust_result": {
            **axiom_classes,
            "policy_pass": policy_pass,
        },
        "missing_declarations": missing,
        "declarations": records,
        "axiom_provenance": [
            axiom_provenance[name] for name in sorted(axiom_provenance)
        ],
        "axiom_dependency_groups": group_axiom_sets(records),
        "limitations": [
            "Coverage is the import closure of the declared compiled entrypoints, not every source module in the repository.",
            "Compiled coverage is enumerated from Lean's exported environment; lexical source declarations are only a cross-check.",
            "The probe reports transitive axioms known to the pinned Lean environment; it does not prove semantic correctness of specifications.",
            "The probe uses an environment allowlist and disposable HOME/TEMP, but this Windows host does not provide OS-enforced network or filesystem isolation.",
            "The probe is launched through the inspected project's lake env; the probe module, module search path, loaded artifacts, and static KEYAI output are not independently authenticated.",
            "This reviewed-source runner does not enforce wall-time, child-process, or output-size limits.",
            "A successful internal build and probe are technical evidence, not customer or external-pilot evidence.",
        ],
    }
    result["probe_sha256"] = sha256_bytes(canonical_json_bytes(result))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        required=True,
        help="disposable built checkout at the pinned source revision",
    )
    parser.add_argument(
        "--contract",
        default=str(DEFAULT_CONTRACT),
        help="canonical portability rehearsal contract",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if the committed compiled probe differs",
    )
    args = parser.parse_args()
    try:
        contract = load_json(Path(args.contract))
        snapshot_path = ROOT / contract["artifacts"]["snapshot"]
        snapshot = load_json(snapshot_path)
        verify_snapshot(snapshot, contract)
        result = build_probe(Path(args.source).resolve(strict=True), contract, snapshot)
        output = artifact_path(contract, "compiled_probe", "compiled-probe.json")
        if args.check:
            if not output.is_file() or load_json(output) != result:
                raise PortabilityError(f"committed compiled probe is stale: {output}")
            print(
                "compiled probe check OK: "
                f"{result['coverage']['found_public_declarations']} declarations, "
                f"{len(result['trust_result']['all'])} axioms"
            )
            return 0
        if output.exists():
            existing = load_json(output)
            if (
                existing.get("rehearsal_id") != contract["id"]
                or existing.get("generator", {}).get("id") != GENERATOR_ID
            ):
                raise PortabilityError(
                    f"refusing to overwrite an unowned artifact: {output}"
                )
        if not result["trust_result"]["policy_pass"]:
            raise PortabilityError(
                "compiled probe policy failed: "
                f"{len(result['missing_declarations'])} missing declarations, "
                f"forbidden={result['trust_result']['forbidden']}, "
                f"unexpected={result['trust_result']['unexpected']}, "
                "invalid allowed provenance="
                f"{result['trust_result']['invalid_allowed_provenance']}, "
                "missing accepted="
                f"{result['trust_result']['missing_accepted_axioms']}, "
                "invalid provenance="
                f"{result['trust_result']['invalid_accepted_provenance']}"
            )
        write_json_atomic(output, result)
        print(
            f"wrote {output.relative_to(ROOT)}: "
            f"{result['coverage']['found_public_declarations']} declarations, "
            f"axioms {result['trust_result']['all']}, "
            f"digest {result['probe_sha256']}"
        )
        return 0
    except (OSError, PortabilityError, ValueError) as exc:
        print(f"compiled probe FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
