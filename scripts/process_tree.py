"""Own and terminate complete subprocess trees on Windows and POSIX."""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from typing import BinaryIO, Iterator


class ProcessCleanupError(ValueError):
    """Ownership or bounded cleanup of a child process tree could not be proven."""


def _macos_group_has_running_members(pgid: int) -> bool:
    """Fail closed unless ps confirms no non-zombie processes in the owned group."""
    try:
        snapshot = subprocess.run(
            ["ps", "-A", "-o", "pgid=", "-o", "stat="],
            stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=5, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ProcessCleanupError("could not inspect process group after macOS signal denial") from exc
    if snapshot.returncode or snapshot.stderr.strip():
        raise ProcessCleanupError("process-group inspection failed after macOS signal denial")
    for row in snapshot.stdout.splitlines():
        fields = row.split()
        if len(fields) != 2 or not fields[0].isdigit():
            raise ProcessCleanupError("unrecognized process-group snapshot")
        if int(fields[0]) == pgid and not fields[1].startswith("Z"):
            return True
    return False


def stop_process_tree(process: subprocess.Popen[bytes]) -> None:
    """Stop only this command's owned tree, with bounded cleanup waits."""
    try:
        if os.name == "nt":
            taskkill = Path(os.environ["SystemRoot"]) / "System32" / "taskkill.exe"
            result = subprocess.run(
                [str(taskkill), "/PID", str(process.pid), "/T", "/F"],
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                timeout=5, check=False,
            )
            if result.returncode:
                raise ProcessCleanupError(f"could not confirm process-tree cleanup for PID {process.pid}")
        else:
            # macOS may deny signals to an already-exited group containing only zombies.
            leader_running = process.poll() is None
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except PermissionError:
                if process.poll() is None:
                    raise  # A still-running leader must not be silently ignored.
                if leader_running:
                    # The leader exited between poll and signal: retry once.
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    except PermissionError:
                        if sys.platform != "darwin" or _macos_group_has_running_members(process.pid):
                            raise
                elif sys.platform != "darwin" or _macos_group_has_running_members(process.pid):
                    raise
            except ProcessLookupError:
                pass
    finally:
        # Reap the immediate child even if tree cleanup itself reports failure.
        if process.poll() is None:
            process.kill()
        process.wait(timeout=5)



@contextmanager
def owned_process(command: list[str], project: Path, environment: dict[str, str], output: BinaryIO, errors: BinaryIO, *, stdin: int = subprocess.PIPE) -> Iterator[subprocess.Popen[bytes]]:
    options = dict(cwd=project, env=environment, stdin=stdin, stdout=output, stderr=errors)
    if os.name != "nt":
        process = subprocess.Popen(command, start_new_session=True, **options)
        try:
            yield process
        finally:
            stop_process_tree(process)
            if process.stdin is not None:
                process.stdin.close()
        return

    # Assign a suspended process before it can create helpers. The Job Object
    # owns every descendant and also kills them if this supervisor is terminated.
    import ctypes
    from ctypes import wintypes

    class ThreadEntry(ctypes.Structure):
        _fields_ = [("size", wintypes.DWORD), ("usage", wintypes.DWORD), ("id", wintypes.DWORD),
                    ("owner", wintypes.DWORD), ("priority", wintypes.LONG),
                    ("delta", wintypes.LONG), ("flags", wintypes.DWORD)]

    class JobAccounting(ctypes.Structure):
        _fields_ = [("user", ctypes.c_int64), ("kernel", ctypes.c_int64),
                    ("period_user", ctypes.c_int64), ("period_kernel", ctypes.c_int64),
                    ("faults", wintypes.DWORD), ("total", wintypes.DWORD),
                    ("active", wintypes.DWORD), ("terminated", wintypes.DWORD)]

    class JobBasicLimits(ctypes.Structure):
        _fields_ = [("process_user_time", ctypes.c_int64), ("job_user_time", ctypes.c_int64),
                    ("flags", wintypes.DWORD), ("minimum_working_set", ctypes.c_size_t),
                    ("maximum_working_set", ctypes.c_size_t), ("active_process_limit", wintypes.DWORD),
                    ("affinity", ctypes.c_size_t), ("priority_class", wintypes.DWORD),
                    ("scheduling_class", wintypes.DWORD)]

    class JobExtendedLimits(ctypes.Structure):
        _fields_ = [("basic", JobBasicLimits), ("io_counters", ctypes.c_uint64 * 6),
                    ("process_memory_limit", ctypes.c_size_t), ("job_memory_limit", ctypes.c_size_t),
                    ("peak_process_memory", ctypes.c_size_t), ("peak_job_memory", ctypes.c_size_t)]

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    signatures = {
        "CreateJobObjectW": ([wintypes.LPVOID, wintypes.LPCWSTR], wintypes.HANDLE),
        "SetInformationJobObject": ([wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD], wintypes.BOOL),
        "AssignProcessToJobObject": ([wintypes.HANDLE, wintypes.HANDLE], wintypes.BOOL),
        "TerminateJobObject": ([wintypes.HANDLE, wintypes.UINT], wintypes.BOOL),
        "QueryInformationJobObject": ([wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD, wintypes.LPVOID], wintypes.BOOL),
        "CreateToolhelp32Snapshot": ([wintypes.DWORD, wintypes.DWORD], wintypes.HANDLE),
        "Thread32First": ([wintypes.HANDLE, ctypes.POINTER(ThreadEntry)], wintypes.BOOL),
        "Thread32Next": ([wintypes.HANDLE, ctypes.POINTER(ThreadEntry)], wintypes.BOOL),
        "OpenThread": ([wintypes.DWORD, wintypes.BOOL, wintypes.DWORD], wintypes.HANDLE),
        "ResumeThread": ([wintypes.HANDLE], wintypes.DWORD),
        "CloseHandle": ([wintypes.HANDLE], wintypes.BOOL),
    }
    for name, (arguments, result) in signatures.items():
        getattr(kernel, name).argtypes = arguments
        getattr(kernel, name).restype = result
    job = kernel.CreateJobObjectW(None, None)
    if not job:
        raise ctypes.WinError(ctypes.get_last_error())
    process, assigned = None, False
    try:
        limits = JobExtendedLimits()
        limits.basic.flags = 0x00002000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        # JobObjectExtendedLimitInformation configures the job before launch.
        if not kernel.SetInformationJobObject(job, 9, ctypes.byref(limits), ctypes.sizeof(limits)):
            raise ctypes.WinError(ctypes.get_last_error())
        process = subprocess.Popen(command, creationflags=0x00000004, **options)  # CREATE_SUSPENDED
        if not kernel.AssignProcessToJobObject(job, int(process._handle)):
            raise ctypes.WinError(ctypes.get_last_error())
        assigned = True
        snapshot = kernel.CreateToolhelp32Snapshot(4, 0)  # TH32CS_SNAPTHREAD
        if snapshot == ctypes.c_void_p(-1).value:
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            entry = ThreadEntry()
            entry.size = ctypes.sizeof(entry)
            found = kernel.Thread32First(snapshot, ctypes.byref(entry))
            while found and entry.owner != process.pid:
                found = kernel.Thread32Next(snapshot, ctypes.byref(entry))
            if not found:
                raise ProcessCleanupError("cannot find the suspended server thread")
            thread = kernel.OpenThread(2, False, entry.id)  # THREAD_SUSPEND_RESUME
            if not thread:
                raise ctypes.WinError(ctypes.get_last_error())
            try:
                if kernel.ResumeThread(thread) == 0xFFFFFFFF:
                    raise ctypes.WinError(ctypes.get_last_error())
            finally:
                kernel.CloseHandle(thread)
        finally:
            kernel.CloseHandle(snapshot)
        yield process
    finally:
        try:
            if assigned:
                if not kernel.TerminateJobObject(job, 1):
                    raise ctypes.WinError(ctypes.get_last_error())
                deadline = time.monotonic() + 5
                accounting = JobAccounting()
                while True:
                    if not kernel.QueryInformationJobObject(job, 1, ctypes.byref(accounting), ctypes.sizeof(accounting), None):
                        raise ctypes.WinError(ctypes.get_last_error())
                    if not accounting.active:
                        break
                    if time.monotonic() >= deadline:
                        raise ProcessCleanupError("server job cleanup exceeded its time limit")
                    time.sleep(0.01)
            elif process is not None:
                process.kill()
            if process is not None:
                process.wait(timeout=5)
        finally:
            kernel.CloseHandle(job)
            if process is not None and process.stdin is not None:
                process.stdin.close()
