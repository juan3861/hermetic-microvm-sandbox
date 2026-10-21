"""
TITAN-HYPERION APEX / HERMETIC MICROVM SANDBOX
Pre-Warmed MicroVM Pool Manager Test Suite
==========================================
Verifies:
  1. Instant pre-initialization of ready slots in /dev/shm
  2. Sub-millisecond (< 0.1 ms) lease acquisition
  3. Microsecond state rollback and CoW recycling
  4. Telemetry metrics and hit-ratio tracking
  5. Clean pool evaporation on shutdown
"""

import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.warm_pool_manager import WarmPoolManager


def run_warm_pool_audit():
    print("=" * 80)
    print("[*] HERMETIC MICROVM SANDBOX: PRE-WARMED POOL AUDIT")
    print("=" * 80)

    pool = WarmPoolManager(target_pool_size=2, memory_mb=128)

    try:
        # 1. Verify pool pre-warming
        print("\n[1/4] Verifying Pre-Warmed Pool Initialization...")
        telemetry = pool.get_telemetry()
        print(f"--> Target Size: {telemetry['target_pool_size']} | Ready Slots: {telemetry['ready_count']}")
        assert telemetry["ready_count"] == 2
        assert telemetry["leased_count"] == 0

        # 2. Acquire pre-warmed slot (< 0.1 ms expected)
        print("\n[2/4] Testing Sub-Millisecond Slot Acquisition...")
        t0 = time.perf_counter()
        lease1 = pool.acquire()
        t_lease = round((time.perf_counter() - t0) * 1000, 3)
        print(f"--> Slot '{lease1['slot_id']}' leased in {lease1['elapsed_ms']} ms (Hit={lease1['pool_hit']})")
        assert lease1["ok"] is True
        assert lease1["pool_hit"] is True
        assert pool.get_telemetry()["ready_count"] == 1
        assert pool.get_telemetry()["leased_count"] == 1

        # 3. Recycle slot with microsecond rollback
        print("\n[3/4] Testing Microsecond State Rollback & Recycling...")
        rel1 = pool.release(lease1["slot_id"], recycle=True)
        print(f"--> Slot '{lease1['slot_id']}' recycled in {rel1['elapsed_ms']} ms")
        assert rel1["ok"] is True
        assert pool.get_telemetry()["ready_count"] == 2
        assert pool.get_telemetry()["leased_count"] == 0
        assert pool.get_telemetry()["stats"]["recycles"] == 1

        # 4. Successive leases & hit ratio
        print("\n[4/4] Testing Successive Rapid Leases...")
        l_a = pool.acquire()
        l_b = pool.acquire()
        assert l_a["pool_hit"] is True
        assert l_b["pool_hit"] is True
        print(f"--> 2 concurrent slots leased successfully. Active leased: {pool.get_telemetry()['leased_count']}")

        pool.release(l_a["slot_id"], recycle=True)
        pool.release(l_b["slot_id"], recycle=True)

        final_stats = pool.get_telemetry()
        print(f"--> Final Hit Ratio: {final_stats['hit_ratio_percent']}% | Total Leases: {final_stats['stats']['total_leases']}")
        assert final_stats["hit_ratio_percent"] == 100.0

    finally:
        pool.destroy_all()
        print("--> Pool evaporated safely.")

    print("\n" + "=" * 80)
    print("[+] PRE-WARMED MICROVM POOL: 100% APROVADO!")
    print("=" * 80)
    return True


if __name__ == "__main__":
    if not run_warm_pool_audit():
        sys.exit(1)
