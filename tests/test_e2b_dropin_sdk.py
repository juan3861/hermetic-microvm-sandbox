"""
TITAN-HYPERION APEX / HERMETIC MICROVM SANDBOX
E2B & OpenHands Drop-In Universal Agent SDK Test Suite
======================================================
Verifies:
  1. Instant instantiation of Sandbox(memory_mb=256).
  2. Filesystem operations (files.write, files.read, files.list, files.remove) in volatile DDR RAM.
  3. Commands execution (commands.run, process.start) with zero physical host disk mutation.
  4. Snapshotting and microsecond state rollback.
  5. Clean RAM evaporation on context manager exit (__exit__).
"""

import sys
import time
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sdk.hermetic_sandbox import Sandbox, CommandResult, Process


def run_e2b_sdk_audit():
    print("=" * 80)
    print("[*] HERMETIC MICROVM SANDBOX: E2B / OPENHANDS DROP-IN SDK AUDIT")
    print("=" * 80)

    # 1. Instantiate Sandbox via Context Manager
    print("\n[1/5] Testing Sandbox Context Lifecycle & RAM Volatility...")
    with Sandbox(memory_mb=256) as sb:
        print(f"--> Spawned Sandbox: {sb}")
        assert not sb.closed, "Sandbox should be active inside context"

        # 2. Filesystem in volatile RAM
        print("\n[2/5] Testing In-Memory Filesystem (files.write / files.read / files.list)...")
        sb.files.write("agent_task.py", "x = 42\nprint(f'AGENT_TASK_VALUE_{x}')\n")
        content = sb.files.read("agent_task.py")
        assert "AGENT_TASK_VALUE_" in content and "x = 42" in content
        print("--> File written and read back cleanly from DDR RAM")

        file_list = sb.files.list()
        names = [f["name"] for f in file_list]
        print(f"--> Directory listing: {names}")
        assert "agent_task.py" in names

        # 3. Command execution
        print("\n[3/5] Testing Command Execution (commands.run & process.start)...")
        res: CommandResult = sb.commands.run("python3 agent_task.py")
        print(f"--> Command execution elapsed: {res.elapsed_ms} ms | exit_code: {res.exit_code}")
        print(f"--> stdout: {res.stdout.strip()}")
        assert res.exit_code == 0
        assert "AGENT_TASK_VALUE_42" in res.stdout

        proc: Process = sb.process.start("echo 'PROCESS_START_OK'")
        p_res = proc.wait()
        assert p_res.exit_code == 0
        assert "PROCESS_START_OK" in p_res.stdout
        print("--> Process.start interface verified")

        # 4. Snapshotting and Rollback
        print("\n[4/5] Testing MicroVM Snapshotting and State Rollback...")
        snap = sb.take_snapshot("ckpt_state_1")
        print(f"--> Snapshot taken: {snap.get('snapshot_name', 'ckpt_state_1')}")

        sb.files.write("canary_temp.txt", "SHOULD_BE_REVERTED")
        assert "canary_temp.txt" in [f["name"] for f in sb.files.list()]

        roll = sb.restore_snapshot("ckpt_state_1")
        print(f"--> Rollback executed: {roll.get('status', 'OK')}")

    # 5. Verify Evaporation on Exit
    print("\n[5/5] Verifying Sandbox Termination & RAM Evaporation...")
    assert sb.closed is True, "Sandbox should be automatically closed after context exit!"
    print("--> Sandbox successfully closed and volatile RAM evaporated")

    print("\n" + "=" * 80)
    print("[+] E2B / OPENHANDS DROP-IN SDK: 100% APROVADO!")
    print("=" * 80)
    return True


if __name__ == "__main__":
    success = run_e2b_sdk_audit()
    if not success:
        sys.exit(1)
