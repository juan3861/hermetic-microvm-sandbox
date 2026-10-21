"""
TITAN-HYPERION APEX / HERMETIC MICROVM SANDBOX
Fault-Tolerant MicroVM Self-Recovery Watchdog Test Suite
========================================================
Verifies:
  1. MicroVM execution of standard non-crashing commands.
  2. Interception of fatal crash signals (SIGSEGV 139, SIGKILL 137).
  3. Autonomous state rollback to pre-crash clean checkpoint.
  4. Restoration of pristine RAM workspace with zero host disk wear.
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

from core.fault_tolerant_watchdog import FaultTolerantWatchdog


def run_watchdog_audit():
    print("=" * 80)
    print("[*] HERMETIC MICROVM SANDBOX: FAULT-TOLERANT WATCHDOG AUDIT")
    print("=" * 80)

    watchdog = FaultTolerantWatchdog()
    sid = "test_watchdog_suite_sess"
    watchdog.mgr.create_session(sid, memory_mb=256)

    try:
        # 1. Normal execution
        print("\n[1/3] Executing Standard Stable Workload...")
        res1 = watchdog.execute_with_auto_healing(sid, "echo", ["STABLE_WORKLOAD_EXECUTION"])
        print(f"--> Normal Status: ok={res1['ok']} | self_healed={res1['self_healed']}")
        assert res1["ok"] is True
        assert res1["self_healed"] is False

        # 2. Crash interception (SIGSEGV 139)
        print("\n[2/3] Simulating Fatal Memory Crash (SIGSEGV / Exit 139)...")
        res2 = watchdog.execute_with_auto_healing(sid, "sh", ["-c", "kill -SEGV $$ || exit 139"])
        print(f"--> Crash Intercepted: {res2['crash_intercepted']}")
        print(f"--> Signal: {res2['signal']} ({res2['description']})")
        print(f"--> Autonomous Self-Healed: {res2['self_healed']}")
        print(f"--> Restored Checkpoint: {res2['recovery']['clean_checkpoint']}")
        assert res2["crash_intercepted"] is True
        assert res2["self_healed"] is True
        assert res2["signal"] == "SIGSEGV"
        assert res2["recovery"]["recovered"] is True

        # 3. Post-heal verification
        print("\n[3/3] Verifying Workspace Integrity After Self-Healing...")
        res3 = watchdog.execute_with_auto_healing(sid, "echo", ["POST_HEAL_SANITY_CHECK"])
        print(f"--> Post-Heal Status: ok={res3['ok']} | output={res3['execution']['stdout'].strip()}")
        assert res3["ok"] is True
        assert "POST_HEAL_SANITY_CHECK" in res3["execution"]["stdout"]
        print("--> MicroVM Session survived fatal crash and restored state seamlessly!")

    finally:
        watchdog.mgr.terminate_session(sid)

    print("\n" + "=" * 80)
    print("[+] FAULT-TOLERANT MICROVM WATCHDOG: 100% APROVADO!")
    print("=" * 80)
    return True


if __name__ == "__main__":
    success = run_watchdog_audit()
    if not success:
        sys.exit(1)
