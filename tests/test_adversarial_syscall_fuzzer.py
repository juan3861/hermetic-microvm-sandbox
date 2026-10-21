"""
TITAN-HYPERION APEX / HERMETIC MICROVM SANDBOX
Adversarial Syscall Fuzzing & Chaos Test Suite
==============================================
Verifies:
  1. Generation of 100 chaotic adversarial syscall and attack vectors.
  2. Complete neutralization of ctypes, raw sockets, cloud metadata exfiltration, and rootkits.
  3. Strict containment score reaching exactly 100.0%.
  4. 0 leaked system calls or uncontained exploits.
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

from security.adversarial_syscall_fuzzer import AdversarialSyscallFuzzer


def run_fuzzer_audit():
    print("=" * 80)
    print("[*] HERMETIC MICROVM SANDBOX: ADVERSARIAL SYSCALL FUZZING AUDIT")
    print("=" * 80)

    fuzzer = AdversarialSyscallFuzzer()

    # 1. Generate probes
    print("\n[1/3] Generating 100 Adversarial Syscall & Chaos Vectors...")
    probes = fuzzer.generate_100_fuzz_probes()
    print(f"--> Total Generated Probes: {len(probes)}")
    assert len(probes) == 100, "Must generate exactly 100 fuzz probes!"

    # 2. Run fuzzing battery
    print("\n[2/3] Firing Syscall Fuzzing Battery Against Sentry Guard...")
    res = fuzzer.run_fuzz_audit()
    print(f"--> Blocked Probes: {res['blocked_probes']} / {res['total_fuzz_probes']}")
    print(f"--> Escaped Probes: {res['escaped_probes']}")
    print(f"--> Containment Score: {res['containment_score_pct']}%")
    print(f"--> Execution Wall Time: {res['elapsed_ms']} ms")
    print("--> Violation Categories Detected:")
    for cat, count in res["violation_categories"].items():
        print(f"    - {cat}: {count} probes")

    # 3. Assert zero-tolerance containment
    print("\n[3/3] Enforcing Zero-Tolerance Quality Gate...")
    assert res["escaped_probes"] == 0, f"Critical Security Failure: {res['escaped_probes']} probes escaped!"
    assert res["containment_score_pct"] == 100.0, "Containment score must be 100.0%!"
    assert res["all_probes_neutralized"] is True

    print("\n" + "=" * 80)
    print("[+] ADVERSARIAL SYSCALL FUZZING: 100% APROVADO!")
    print("=" * 80)
    return True


if __name__ == "__main__":
    success = run_fuzzer_audit()
    if not success:
        sys.exit(1)
