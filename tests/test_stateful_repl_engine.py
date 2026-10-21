"""
TITAN-HYPERION APEX / HERMETIC MICROVM SANDBOX
Stateful Interactive REPL & Code Interpreter Test Suite
======================================================
Verifies:
  1. Persistent variable namespace across sequential executions
  2. Multi-step algorithmic computations and function declarations
  3. Clean separation of stdout/stderr streams
  4. Exception handling without session crash
  5. Integration with top-level Sandbox.run_code() API
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.stateful_repl_engine import StatefulREPLEngine
from sdk.hermetic_sandbox import Sandbox


def run_repl_audit():
    print("=" * 80)
    print("[*] HERMETIC MICROVM SANDBOX: STATEFUL REPL INTERPRETER AUDIT")
    print("=" * 80)

    engine = StatefulREPLEngine(session_id="audit_repl_sess")

    # 1. State persistence
    print("\n[1/5] Testing Variable Persistence Across Executions...")
    res1 = engine.execute_code("agent_token = 987654\nbase_scale = 10")
    print(f"--> Step 1 elapsed: {res1.elapsed_ms} ms | Result: {res1.result}")
    assert res1.error is None

    res2 = engine.execute_code("agent_token * base_scale")
    print(f"--> Step 2 elapsed: {res2.elapsed_ms} ms | Value: {res2.result}")
    assert res2.result == 9876540
    assert res2.text == "9876540"

    # 2. Function declaration and execution
    print("\n[2/5] Testing Function Declaration & Calling Across Steps...")
    res3 = engine.execute_code("def compute_hypotenuse(a, b):\n    return (a**2 + b**2)**0.5")
    assert res3.error is None
    res4 = engine.execute_code("compute_hypotenuse(3, 4)")
    print(f"--> Function evaluated: {res4.result}")
    assert res4.result == 5.0

    # 3. Stdout stream capture
    print("\n[3/5] Testing Stdout Stream Capture...")
    res5 = engine.execute_code("print('STREAMED_AGENT_LOG_PAYLOAD')\n'RETURN_VALUE'")
    print(f"--> Stdout captured: {res5.stdout.strip()}")
    assert "STREAMED_AGENT_LOG_PAYLOAD" in res5.stdout
    assert res5.result == "RETURN_VALUE"

    # 4. Exception containment
    print("\n[4/5] Testing Exception Containment...")
    res6 = engine.execute_code("100 / 0")
    print(f"--> Captured expected error: {res6.error}")
    assert "ZeroDivisionError" in str(res6.error)
    # Session must still be alive
    res7 = engine.execute_code("agent_token")
    assert res7.result == 987654

    # 5. Drop-in Sandbox.run_code() API
    print("\n[5/5] Testing Drop-In Sandbox.run_code() Integration...")
    with Sandbox(memory_mb=128) as sb:
        sb_res1 = sb.run_code("sandbox_state = 'PRISTINE_RAM_INITIALIZED'")
        assert sb_res1.error is None
        sb_res2 = sb.run_code("sandbox_state + ' -> VERIFIED'")
        print(f"--> Sandbox REPL evaluated: {sb_res2.text}")
        assert sb_res2.result == "PRISTINE_RAM_INITIALIZED -> VERIFIED"

    print("\n" + "=" * 80)
    print("[+] STATEFUL REPL CODE INTERPRETER: 100% APROVADO!")
    print("=" * 80)
    return True


if __name__ == "__main__":
    if not run_repl_audit():
        sys.exit(1)
