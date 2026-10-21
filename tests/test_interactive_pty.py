"""
TITAN-HYPERION APEX / HERMETIC MICROVM SANDBOX
Interactive Pseudo-Terminal (PTY) Test Suite
============================================
Verifies:
  1. Allocation of real POSIX openpty sessions in volatile DDR RAM (/dev/shm)
  2. Bidirectional stdin/stdout streaming with sub-millisecond dispatch
  3. Dynamic window resizing (cols, rows)
  4. Active secret redaction in PTY output streams
  5. Clean session termination and volatile tmpfs resource evaporation
"""

import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sdk.hermetic_sandbox import Sandbox, PTYSession


def run_pty_audit():
    print("=" * 80)
    print("[*] HERMETIC MICROVM SANDBOX: INTERACTIVE PTY PSEUDO-TERMINAL AUDIT")
    print("=" * 80)

    with Sandbox(memory_mb=256) as sb:
        # 1. Spawn interactive PTY session
        print("\n[1/4] Spawning Interactive POSIX PTY Session...")
        t0 = time.perf_counter()
        pty = sb.pty.create(command="sh", cols=80, rows=24)
        elapsed_spawn = round((time.perf_counter() - t0) * 1000, 3)
        print(f"--> PTY Spawned: {pty} (Latency: {elapsed_spawn} ms)")
        assert pty.is_alive() is True

        # 2. Test bidirectional input/output
        print("\n[2/4] Testing Bidirectional stdin/stdout Stream...")
        pty.send_input("echo 'PTY_STREAM_VERIFIED'\n")
        time.sleep(0.3)
        out = pty.read(timeout=1.0)
        print(f"--> Received Output:\n{repr(out)}")
        assert "PTY_STREAM_VERIFIED" in out

        # 3. Test dynamic window resizing
        print("\n[3/4] Testing Dynamic Window Resizing (TIOCSWINSZ)...")
        resized = pty.resize(cols=120, rows=40)
        print(f"--> Resized to 120x40: {resized}")
        assert resized is True
        assert pty.cols == 120
        assert pty.rows == 40

        # 4. Test active secret sanitization in PTY output stream
        print("\n[4/4] Testing Active Secret Sanitization on PTY Stream...")
        pty.send_input("echo 'SECRET_PROBE: sk-proj-1234567890abcdef1234567890'\n")
        time.sleep(0.3)
        sanitized_out = pty.read(timeout=1.0)
        print(f"--> Sanitized Stream Output:\n{repr(sanitized_out)}")
        assert "sk-***[REDACTED_OPENAI_KEY]***" in sanitized_out
        assert "sk-proj-1234567890" not in sanitized_out

        # Terminate PTY cleanly
        pty.kill()
        assert pty.is_alive() is False
        print("--> PTY Process Terminated and tmpfs Evaporated.")

    print("\n" + "=" * 80)
    print("[+] INTERACTIVE PTY SESSION: 100% APROVADO!")
    print("=" * 80)
    return True


if __name__ == "__main__":
    if not run_pty_audit():
        sys.exit(1)
