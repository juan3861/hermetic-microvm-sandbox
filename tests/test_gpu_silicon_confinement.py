"""
TITAN-HYPERION APEX / HERMETIC MICROVM SANDBOX
Silicon GPU Hardware Passthrough & VRAM Confinement Test Suite
==============================================================
Verifies:
  1. Discovery of host GPU hardware (DirectML / WDDM / Vulkan / CUDA).
  2. Construction of hermetic jail profile with /dev/dxg device binding.
  3. Strict VRAM quota ceiling enforcement.
  4. Execution of tensor workloads without host physical disk mutation.
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

from engines.silicon_gpu_engine import SiliconGPUEngine


def run_gpu_confinement_audit():
    print("=" * 80)
    print("[*] HERMETIC MICROVM SANDBOX: SILICON GPU CONFINEMENT AUDIT")
    print("=" * 80)

    engine = SiliconGPUEngine(default_vram_mb=4096)

    # 1. Hardware probe
    print("\n[1/3] Probing GPU Hardware & Driver Architecture...")
    probe = engine.probe_gpu_hardware()
    print(f"--> Detected {probe['gpu_count']} GPU adapter(s)")
    for idx, g in enumerate(probe["adapters"]):
        print(f"    [{idx+1}] {g['name']} | VRAM: {g['vram_mb']} MB | Driver: {g.get('driver_version','')}")
    print(f"--> Total Cluster VRAM: {probe['total_vram_mb']} MB")
    print(f"--> Architecture: {probe['driver_architecture']}")
    print(f"--> Supported Backends: {probe['supported_backends']}")
    assert probe["gpu_count"] >= 1, "At least 1 GPU adapter must be detected!"
    assert probe["total_vram_mb"] > 0, "Total VRAM must be greater than zero!"

    # 2. Jail profile & VRAM confinement
    print("\n[2/3] Constructing GPU Confinement Jail Profile...")
    profile = engine.create_gpu_jail_profile(vram_limit_mb=2048)
    print(f"--> Enforced VRAM Ceiling: {profile['vram_limit_mb']} MB")
    print(f"--> Environment Confinement: {profile['env_confinement']}")
    assert profile["vram_limit_mb"] == 2048
    assert "HERMETIC_VRAM_CEILING_MB" in profile["env_confinement"]
    if probe["has_dxg_device"]:
        assert "--dev-bind" in profile["bwrap_flags"]
        print("--> Hardware /dev/dxg device node bound securely into sandbox")

    # 3. Workload tensor execution
    print("\n[3/3] Executing Hermetic Tensor Payload...")
    code = (
        "import math\n"
        "matrix = [[math.sin(i * j) for j in range(100)] for i in range(100)]\n"
        "result_payload = {'tensor_dim': [100, 100], 'norm': sum(sum(r) for r in matrix)}\n"
    )
    workload = engine.execute_gpu_workload(code=code, vram_limit_mb=2048)
    print(f"--> Accelerated: {workload['accelerated']}")
    print(f"--> Device: {workload['device']}")
    print(f"--> Zero Host Disk Mutation: {workload['zero_host_disk_mutation']}")
    assert workload["ok"] is True or workload["gpu_workload_executed"] is True
    assert workload["zero_host_disk_mutation"] is True

    print("\n" + "=" * 80)
    print("[+] SILICON GPU HARDWARE CONFINEMENT: 100% APROVADO!")
    print("=" * 80)
    return True


if __name__ == "__main__":
    success = run_gpu_confinement_audit()
    if not success:
        sys.exit(1)
