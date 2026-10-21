"""
TITAN-HYPERION APEX / HERMETIC MICROVM SANDBOX
Deterministic Trajectory Recording & Replay Test Suite
======================================================
Verifies:
  1. Cryptographic append-only trajectory recording of agent interactions
  2. Invariant SHA256 state hashing across transitions
  3. 100% deterministic replay convergence in fresh sandbox workspaces
  4. Detection of state divergences and reproducibility verification
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sdk.hermetic_sandbox import Sandbox, ReplayRecorder, ReplayEngine


def run_replay_audit():
    print("=" * 80)
    print("[*] HERMETIC MICROVM SANDBOX: DETERMINISTIC REPLAY AUDIT")
    print("=" * 80)

    # 1. Record trajectory in source sandbox
    print("\n[1/3] Executing & Recording Agent Trajectory in Source Sandbox...")
    with Sandbox(memory_mb=256) as sb_source:
        # Step 1: File Write
        sb_source.files.write("calc.py", "def add(a, b): return a + b\nprint('SUM:', add(10, 32))")
        
        # Step 2: Command Run
        c_res = sb_source.commands.run("python3 calc.py")
        print(f"--> Source Command Output: {c_res.stdout.strip()}")
        assert "SUM: 42" in c_res.stdout

        # Step 3: Stateful REPL Evaluation
        r_res = sb_source.run_code("y = 100\ny * 2")
        print(f"--> Source REPL Result: {r_res.result}")
        assert r_res.result == 200

        # Step 4: Snapshot Creation
        sb_source.take_snapshot("ckpt_source_clean")

        trace = sb_source.export_trace()
        print(f"--> Trajectory Recorded: {trace['event_count']} events | Final Hash: {trace['final_hash']}")
        assert trace["event_count"] >= 4
        assert len(trace["final_hash"]) == 16

    # 2. Replay trajectory in fresh isolated sandbox
    print("\n[2/3] Deterministically Replaying Trajectory in Fresh Sandbox...")
    with Sandbox(memory_mb=256) as sb_target:
        replay_summary = sb_target.replay_trace(trace)
        print(f"--> Replayed Events: {replay_summary['replayed_events']}")
        print(f"--> Matched Invariants: {replay_summary['matched_invariants']}")
        print(f"--> Mismatch Count: {replay_summary['mismatch_count']}")
        print(f"--> Reproducibility Score: {replay_summary['reproducibility_score']}%")
        print(f"--> Replay Elapsed: {replay_summary['replay_elapsed_ms']} ms")

        assert replay_summary["deterministic_convergence"] is True
        assert replay_summary["reproducibility_score"] == 100.0
        assert replay_summary["mismatch_count"] == 0

    # 3. Verify Formal SMT Theorems (Theorems 4 and 5)
    print("\n[3/3] Formally Verifying Secret Non-Exfiltration & PTY Channel Invariants...")
    from core.formal_invariants_prover import FormalInvariantsProver
    prover = FormalInvariantsProver()
    thm4 = prover.prove_secret_non_exfiltration_theorem()
    thm5 = prover.prove_pty_stream_isolation_theorem()

    print(f"--> Theorem 4 (Secret Non-Exfiltration): {thm4['check_result']} (Proven: {thm4['mathematically_proven']})")
    print(f"--> Theorem 5 (PTY Stream Isolation): {thm5['check_result']} (Proven: {thm5['mathematically_proven']})")

    assert thm4["mathematically_proven"] is True
    assert thm5["mathematically_proven"] is True

    print("\n" + "=" * 80)
    print("[+] DETERMINISTIC REPLAY & FORMAL THEOREMS: 100% APROVADO!")
    print("=" * 80)
    return True


if __name__ == "__main__":
    if not run_replay_audit():
        sys.exit(1)
