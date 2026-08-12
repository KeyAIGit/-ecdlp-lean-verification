from __future__ import annotations

import hashlib
import os
import re
import signal
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from experiments.ecdlp_lab.orchestration import process
from experiments.ecdlp_lab.orchestration.process import (
    ProcessBoundaryError,
    ProcessLimits,
    ProcessTreeEnforcementUnavailable,
    ResourceEnforcementUnavailable,
    WorkerCodeEntry,
    WorkerModules,
    WorkerSourceDrift,
    run_worker,
)


WORKER_SOURCE = r'''
import json
import os
import subprocess
import sys
import time

payload = json.load(sys.stdin)
action = payload.get("action", "echo")

if action == "crash":
    os._exit(7)
if action == "invalid_json":
    sys.stdout.write("{")
    sys.stdout.flush()
    raise SystemExit(0)
if action == "noncanonical_json":
    sys.stdout.write(json.dumps({"z": 1, "a": 2}))
    sys.stdout.flush()
    raise SystemExit(0)
if action == "deep_json":
    sys.stdout.write('{"x":' + '[' * 2000 + '0' + ']' * 2000 + '}')
    sys.stdout.flush()
    raise SystemExit(0)
if action == "stdout_overflow":
    sys.stdout.write("x" * int(payload["size"]))
    sys.stdout.flush()
    time.sleep(10)
if action == "stderr_overflow":
    sys.stderr.write("e" * int(payload["size"]))
    sys.stderr.flush()
    time.sleep(10)
if action == "sleep":
    time.sleep(10)
if action == "orphan":
    child = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(60)"],
        close_fds=True,
    )
    sys.stderr.write(f"CHILD_PID={child.pid}\n")
    sys.stderr.flush()
    time.sleep(10)
if action == "return_with_orphan":
    child = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(60)"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        close_fds=True,
    )
    sys.stderr.write(f"CHILD_PID={child.pid}\n")
    sys.stderr.flush()
if action == "escaped_session":
    child = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(60)"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        close_fds=True,
        start_new_session=True,
    )
    sys.stderr.write(f"CHILD_PID={child.pid}\n")
    sys.stderr.flush()
    time.sleep(60)
if action == "double_fork":
    first = os.fork()
    if first == 0:
        os.setsid()
        second = os.fork()
        if second == 0:
            sys.stderr.write(f"CHILD_PID={os.getpid()}\n")
            sys.stderr.flush()
            time.sleep(60)
            os._exit(0)
        os._exit(0)
    time.sleep(60)
if action == "runtime_paths":
    result = {
        "cwd": os.getcwd(),
        "pythonpath": os.environ.get("PYTHONPATH"),
        "sys_path": sys.path,
    }
    sys.stdout.write(json.dumps(result, sort_keys=True, separators=(",", ":")))
    sys.stdout.flush()
    raise SystemExit(0)

result = {
    "canary": os.environ.get("ECDLP_SECRET_CANARY"),
    "home": os.environ.get("HOME"),
    "payload": payload,
    "tmp": os.environ.get("TMPDIR"),
}
sys.stdout.write(json.dumps(result, sort_keys=True, separators=(",", ":")))
sys.stdout.flush()
'''


def code_entry(root: Path, relative_path: str) -> WorkerCodeEntry:
    payload = (root / relative_path).read_bytes()
    return WorkerCodeEntry(
        relative_path=relative_path,
        sha256=hashlib.sha256(payload).hexdigest(),
        size_bytes=len(payload),
    )


def code_entries(
    root: Path,
    package: str = "testworkers",
    module_names: tuple[str, ...] = ("worker",),
) -> tuple[WorkerCodeEntry, ...]:
    return tuple(
        sorted(
            (
                code_entry(root, f"{package}/__init__.py"),
                *(code_entry(root, f"{package}/{name}.py") for name in module_names),
            ),
            key=lambda entry: entry.relative_path,
        )
    )


def limits(**changes: int) -> ProcessLimits:
    values = {
        "memory_bytes": 256 * 1024 * 1024,
        "timeout_ns": 2_000_000_000,
        "term_grace_ns": 100_000_000,
        "max_stdin_bytes": 64 * 1024,
        "max_stdout_bytes": 64 * 1024,
        "max_stderr_bytes": 16 * 1024,
        "max_json_bytes": 64 * 1024,
    }
    values.update(changes)
    return ProcessLimits(**values)


def process_gone(pid: int) -> bool:
    # The test container may expose host PIDs in procfs while process APIs use
    # an inner PID namespace.  Exercise the same identity-safe proc mapping as
    # the boundary instead of assuming that ``/proc/<inner-pid>`` is valid.
    record = process._proc_record(pid)
    return record is None or record.state == "Z"


@unittest.skipUnless(
    process.memory_enforcement_available()
    and process.process_tree_enforcement_available(),
    "Linux RLIMIT_AS and subreaper/procfs enforcement required",
)
class P04ProcessBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        package = self.root / "testworkers"
        package.mkdir()
        (package / "__init__.py").write_text("", encoding="utf-8")
        (package / "worker.py").write_text(WORKER_SOURCE, encoding="utf-8")
        self.scratch = self.root / "scratch"
        self.modules = WorkerModules(
            method="testworkers.worker",
            validator="testworkers.worker",
            python_path=self.root,
            method_files=code_entries(self.root),
            validator_files=code_entries(self.root),
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def invoke(self, payload: dict[str, object], **limit_changes: int):
        return run_worker(
            "method",
            payload,
            worker_modules=self.modules,
            limits=limits(**limit_changes),
            scratch_root=self.scratch,
        )

    def test_canonical_roundtrip_scrubs_environment_and_isolates_home_tmp(self) -> None:
        payload = {"action": "echo", "nested": {"b": 2, "a": 1}}
        with patch.dict(os.environ, {"ECDLP_SECRET_CANARY": "DO-NOT-INHERIT"}):
            result = self.invoke(payload)
        self.assertTrue(result.passed, result)
        self.assertEqual(result.output["payload"], payload)
        self.assertIsNone(result.output["canary"])
        self.assertTrue(result.output["home"].startswith(str(self.scratch)))
        self.assertTrue(result.output["tmp"].startswith(str(self.scratch)))
        self.assertEqual(result.stderr_bytes, 0)
        self.assertRegex(result.stdout_sha256, r"^[0-9a-f]{64}$")
        self.assertFalse(any(self.scratch.iterdir()))

    def test_role_and_module_are_code_owned_not_payload_commands(self) -> None:
        payload = {
            "action": "echo",
            "module": "os",
            "argv": ["touch", "owned"],
            "command": "touch owned",
        }
        result = self.invoke(payload)
        self.assertTrue(result.passed)
        self.assertEqual(result.output["payload"], payload)
        self.assertFalse((self.root / "owned").exists())
        with self.assertRaises(ProcessBoundaryError):
            run_worker(
                "uploader",
                payload,
                worker_modules=self.modules,
                limits=limits(),
                scratch_root=self.scratch,
            )
        with self.assertRaises(ProcessBoundaryError):
            WorkerModules(
                method="worker;touch.owned",
                validator="testworkers.worker",
                python_path=self.root,
                method_files=self.modules.method_files,
                validator_files=self.modules.validator_files,
            )

    def test_noncanonical_or_malformed_stdout_fails_closed(self) -> None:
        for action in ("invalid_json", "noncanonical_json"):
            with self.subTest(action=action):
                result = self.invoke({"action": action})
                self.assertEqual(result.status, "invalid_output")
                self.assertIsNone(result.output)

    def test_deep_json_output_is_bounded_invalid_output(self) -> None:
        result = self.invoke({"action": "deep_json"})
        self.assertEqual(result.status, "invalid_output")
        self.assertIsNone(result.output)

    def test_worker_crash_is_bounded_and_does_not_echo_an_exception(self) -> None:
        result = self.invoke({"action": "crash"})
        self.assertEqual(result.status, "worker_error")
        self.assertEqual(result.returncode, 7)
        self.assertIsNone(result.output)

    def test_stdout_and_stderr_limits_terminate_the_tree(self) -> None:
        for action, changes in (
            (
                "stdout_overflow",
                {"max_stdout_bytes": 64, "max_json_bytes": 64},
            ),
            ("stderr_overflow", {"max_stderr_bytes": 64}),
        ):
            with self.subTest(action=action):
                result = self.invoke(
                    {"action": action, "size": 4096}, **changes
                )
                self.assertEqual(result.status, "output_limit")
                self.assertTrue(result.terminated)
                self.assertLessEqual(
                    len(result.stderr_excerpt.encode("utf-8")),
                    changes.get("max_stderr_bytes", 16 * 1024),
                )

    def test_timeout_terms_then_kills_orphan_process_group(self) -> None:
        result = self.invoke(
            {"action": "orphan"},
            timeout_ns=250_000_000,
            term_grace_ns=50_000_000,
        )
        self.assertEqual(result.status, "timeout")
        self.assertTrue(result.timed_out)
        self.assertTrue(result.terminated)
        match = re.search(r"CHILD_PID=(\d+)", result.stderr_excerpt)
        self.assertIsNotNone(match, result.stderr_excerpt)
        child_pid = int(match.group(1))
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline and not process_gone(child_pid):
            time.sleep(0.02)
        self.assertTrue(process_gone(child_pid), f"orphan {child_pid} survived")

    def test_successful_leader_with_orphan_is_killed_and_rejected(self) -> None:
        result = self.invoke({"action": "return_with_orphan"})
        self.assertEqual(result.status, "orphan_process")
        self.assertIsNone(result.output)
        self.assertTrue(result.terminated)
        match = re.search(r"CHILD_PID=(\d+)", result.stderr_excerpt)
        self.assertIsNotNone(match, result.stderr_excerpt)
        child_pid = int(match.group(1))
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline and not process_gone(child_pid):
            time.sleep(0.02)
        self.assertTrue(process_gone(child_pid), f"orphan {child_pid} survived")

    def test_setsid_and_double_fork_descendants_cannot_escape(self) -> None:
        for action in ("escaped_session", "double_fork"):
            child_pid: int | None = None
            try:
                result = self.invoke(
                    {"action": action},
                    timeout_ns=300_000_000,
                    term_grace_ns=50_000_000,
                )
                self.assertEqual(result.status, "timeout", result)
                match = re.search(r"CHILD_PID=(\d+)", result.stderr_excerpt)
                self.assertIsNotNone(match, result.stderr_excerpt)
                child_pid = int(match.group(1))
                self.assertTrue(
                    process_gone(child_pid),
                    f"{action} descendant {child_pid} survived",
                )
            finally:
                if child_pid is not None and not process_gone(child_pid):
                    try:
                        os.kill(child_pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass

    def test_child_runtime_contains_only_staged_paths(self) -> None:
        result = self.invoke({"action": "runtime_paths"})
        self.assertTrue(result.passed, result)
        observations = [
            result.output["cwd"],
            result.output["pythonpath"],
            *result.output["sys_path"],
        ]
        for value in observations:
            if value.startswith(str(self.root)):
                self.assertTrue(value.startswith(str(self.scratch)), value)
        self.assertTrue(result.output["pythonpath"].startswith(str(self.scratch)))

    def test_changed_source_is_rejected_before_spawn(self) -> None:
        source = self.root / "testworkers/worker.py"
        source.write_text(WORKER_SOURCE + "\n# drift\n", encoding="utf-8")
        with patch.object(process.subprocess, "Popen") as popen:
            with self.assertRaises(WorkerSourceDrift):
                self.invoke({"action": "echo"})
        popen.assert_not_called()

    def test_manifest_must_include_existing_package_initializers(self) -> None:
        worker_only = (code_entry(self.root, "testworkers/worker.py"),)
        with self.assertRaisesRegex(ProcessBoundaryError, "initializer"):
            WorkerModules(
                method="testworkers.worker",
                validator="testworkers.worker",
                python_path=self.root,
                method_files=worker_only,
                validator_files=worker_only,
            )

    def test_json_limit_is_distinct_from_stream_limit(self) -> None:
        result = self.invoke(
            {"action": "echo", "padding": "x" * 512},
            max_stdout_bytes=4096,
            max_json_bytes=128,
        )
        self.assertEqual(result.status, "output_limit")
        self.assertFalse(result.terminated)

    def test_oversized_or_float_stdin_is_rejected_before_spawn(self) -> None:
        with self.assertRaises(ProcessBoundaryError):
            self.invoke({"action": "echo", "padding": "x" * 1024}, max_stdin_bytes=64)
        with self.assertRaises(ProcessBoundaryError):
            self.invoke({"action": "echo", "bad": 1.5})


class P04ProcessFailClosedTests(unittest.TestCase):
    def test_memory_enforcement_unavailable_fails_before_popen(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            package = root / "example"
            package.mkdir()
            (package / "__init__.py").write_text("", encoding="utf-8")
            (package / "method_worker.py").write_text("", encoding="utf-8")
            (package / "validator_worker.py").write_text("", encoding="utf-8")
            modules = WorkerModules(
                method="example.method_worker",
                validator="example.validator_worker",
                python_path=root,
                method_files=code_entries(root, "example", ("method_worker",)),
                validator_files=code_entries(
                    root, "example", ("validator_worker",)
                ),
            )
            with patch.object(process, "_resource", None), patch.object(
                process.subprocess, "Popen"
            ) as popen:
                with self.assertRaises(ResourceEnforcementUnavailable):
                    run_worker(
                        "method",
                        {"value": 1},
                        worker_modules=modules,
                        limits=limits(),
                        scratch_root=root / "scratch",
                    )
            popen.assert_not_called()

    def test_limit_types_and_relative_module_names_are_rejected(self) -> None:
        with self.assertRaises(ProcessBoundaryError):
            ProcessLimits(memory_bytes=True, timeout_ns=1)
        with tempfile.TemporaryDirectory() as raw:
            with self.assertRaises(ProcessBoundaryError):
                WorkerModules(
                    method="worker",
                    validator="example.validator",
                    python_path=Path(raw),
                    method_files=(),
                    validator_files=(),
                )

    def test_process_tree_enforcement_unavailable_fails_before_popen(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            package = root / "example"
            package.mkdir()
            (package / "__init__.py").write_text("", encoding="utf-8")
            (package / "worker.py").write_text("", encoding="utf-8")
            entries = code_entries(root, "example")
            modules = WorkerModules(
                method="example.worker",
                validator="example.worker",
                python_path=root,
                method_files=entries,
                validator_files=entries,
            )
            with patch.object(process, "_PRCTL", None), patch.object(
                process.subprocess, "Popen"
            ) as popen:
                with self.assertRaises(ProcessTreeEnforcementUnavailable):
                    run_worker(
                        "method",
                        {},
                        worker_modules=modules,
                        limits=limits(),
                        scratch_root=root / "scratch",
                    )
            popen.assert_not_called()


if __name__ == "__main__":
    unittest.main()
