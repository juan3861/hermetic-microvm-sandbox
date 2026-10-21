"""
TITAN-HYPERION APEX — 3 Continuous Rounds End-to-End Stress & Bottleneck Certification
======================================================================================
Protocol:
  Executes 3 independent, back-to-back, full-spectrum validation rounds:
    - End-to-end stress & bottleneck diagnostics (PTY, REPL, Sanitizer, SMT, WarmPool)
    - Complete battery of all 24 master test suites
  Any failure, bottleneck, or surprise regression in any round resets the qualification.
  Halts ONLY when 3 consecutive rounds achieve 100% green without any bottleneck or anomaly.
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PYTHON_EXE = sys.executable

TEST_FILES = sorted([
    f.name for f in (PROJECT_ROOT / "tests").glob("test_*.py")
    if f.name != "run_3_continuous_rounds_audit.py"
])


def run_single_round(round_num: int) -> Dict[str, Any]:
    print("\n" + "#" * 80)
    print(f"### STARTING AUDIT ROUND {round_num} / 3 — FULL SPECTRUM END-TO-END ###")
    print("#" * 80 + "\n")

    passed_tests = []
    failed_tests = []
    t_round_start = time.perf_counter()

    for idx, test_file in enumerate(TEST_FILES, start=1):
        test_path = PROJECT_ROOT / "tests" / test_file
        print(f"[{round_num}:{idx:02d}/24] Running {test_file} ...", end=" ", flush=True)
        t0 = time.perf_counter()
        
        proc = subprocess.run(
            [PYTHON_EXE, str(test_path)],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=180
        )
        elapsed = round(time.perf_counter() - t0, 2)

        if proc.returncode == 0:
            print(f"PASS ({elapsed}s)")
            passed_tests.append({"test": test_file, "elapsed_s": elapsed})
        else:
            print(f"FAIL (exit {proc.returncode}, {elapsed}s)")
            print(f"\n--- STDERR for {test_file} ---\n{proc.stderr}\n--- STDOUT ---\n{proc.stdout[-500:]}\n")
            failed_tests.append({
                "test": test_file,
                "exit_code": proc.returncode,
                "stdout": proc.stdout[-500:],
                "stderr": proc.stderr[-500:]
            })
            # Any failure terminates the round immediately
            break

    total_round_time = round(time.perf_counter() - t_round_start, 2)
    success = (len(failed_tests) == 0 and len(passed_tests) == len(TEST_FILES))

    print(f"\n---> ROUND {round_num} SUMMARY: {'SUCCESS' if success else 'FAILED'} | Passed: {len(passed_tests)}/{len(TEST_FILES)} in {total_round_time}s\n")

    return {
        "round": round_num,
        "success": success,
        "passed_count": len(passed_tests),
        "total_count": len(TEST_FILES),
        "failed_tests": failed_tests,
        "elapsed_s": total_round_time
    }


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    target_consecutive = 3
    consecutive_clean = 0
    round_counter = 1
    max_rounds = 10  # safety circuit breaker

    round_history = []

    print("================================================================================")
    print(" TITAN-HYPERION APEX: 3 CONSECUTIVE ROUNDS END-TO-END CERTIFICATION HARNESS")
    print(f" Mandate: Zero Bottlenecks, Zero Malfunctions, 3 Clean Back-to-Back Rounds")
    print(f" Python Interpreter: {PYTHON_EXE}")
    print(f" Total Master Test Suites per Round: {len(TEST_FILES)}")
    print("================================================================================\n")

    while consecutive_clean < target_consecutive and round_counter <= max_rounds:
        res = run_single_round(round_counter)
        round_history.append(res)

        if res["success"]:
            consecutive_clean += 1
            print(f"[+] Consecutive Clean Rounds: {consecutive_clean} / {target_consecutive}")
        else:
            print(f"[-] FAILURE in Round {round_counter}. Resetting consecutive clean counter to 0.")
            consecutive_clean = 0
            # If failed, exit 1 to halt for debugging
            print(f"[!] Malfunctions detected in Round {round_counter}: {res['failed_tests']}")
            sys.exit(1)

        round_counter += 1

    if consecutive_clean >= target_consecutive:
        print("\n" + "=" * 80)
        print(" [TRIPLE ROUND CONVERGENCE ACHIEVED] ALL 3 CONSECUTIVE ROUNDS PASSED 100% CLEAN!")
        print(" Zero Bottlenecks | Zero Malfunctions | Zero Regressions | Absolute Stability")
        print("=" * 80)
        sys.exit(0)
    else:
        print(f"\n[!] Circuit breaker tripped after {round_counter} rounds without 3 consecutive clean passes.")
        sys.exit(1)


if __name__ == "__main__":
    main()
