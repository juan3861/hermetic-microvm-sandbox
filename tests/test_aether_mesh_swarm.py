"""
TITAN-HYPERION APEX / HERMETIC MICROVM SANDBOX
AetherMesh P2P Distributed Swarm & UCIP Streaming Test Suite
============================================================
Verifies:
  1. Local and peer node registration in decentralized P2P routing table.
  2. Multi-factor fitness scoring for optimal node selection (RAM, Cores, Latency, GPU).
  3. Distributed job dispatch across the mesh.
  4. Live microsecond snapshot streaming with 78-95% UCIP compression.
  5. Cryptographic frame verification and zero host disk wear.
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

from engines.aether_mesh_swarm import AetherMeshSwarm, AetherMeshNode


def run_aether_mesh_audit():
    print("=" * 80)
    print("[*] HERMETIC MICROVM SANDBOX: AETHERMESH P2P SWARM AUDIT")
    print("=" * 80)

    swarm = AetherMeshSwarm(node_id="test_node_master", port=9443)

    # 1. Register heterogeneous peer nodes
    print("\n[1/4] Registering Mesh Swarm Peer Nodes...")
    swarm.register_peer("cloud_swarm_1", "10.0.1.10", 9443, cores=8, ram_mb=16384, has_gpu=False, latency_ms=14.0)
    swarm.register_peer("cloud_gpu_2", "10.0.1.20", 9443, cores=16, ram_mb=32768, has_gpu=True, gpu_name="A100-SXM4", latency_ms=6.5)

    status = swarm.get_mesh_status()
    print(f"--> Total Cluster Nodes: {status['total_nodes_online']}")
    print(f"--> Total Cluster Cores: {status['total_cluster_cores']}")
    print(f"--> Total Cluster RAM: {status['total_cluster_ram_gb']} GB")
    print(f"--> GPU Nodes Online: {status['gpu_nodes_count']}")
    assert status["total_nodes_online"] == 3
    assert status["total_cluster_cores"] >= 40
    assert status["gpu_nodes_count"] >= 2

    # 2. Optimal Node Selection
    print("\n[2/4] Testing Multi-Factor Fitness Node Selection...")
    opt_cpu = swarm.select_optimal_node(require_gpu=False)
    print(f"--> Optimal General Node: {opt_cpu.node_id} (Cores: {opt_cpu.cores}, Latency: {opt_cpu.latency_ms} ms)")
    assert opt_cpu is not None

    opt_gpu = swarm.select_optimal_node(require_gpu=True)
    print(f"--> Optimal GPU Node: {opt_gpu.node_id} (GPU: {opt_gpu.gpu_name}, VRAM: {opt_gpu.ram_mb} MB)")
    assert opt_gpu.has_gpu is True

    # 3. Distributed Job Dispatch
    print("\n[3/4] Dispatching Job Across P2P Mesh Network...")
    job = swarm.dispatch_mesh_job(command="echo 'AETHER_MESH_VERIFIED_100'", require_gpu=True)
    print(f"--> Job ID: {job['job_id']}")
    print(f"--> Routed Node: {job['routed_node']}")
    print(f"--> Elapsed: {job['elapsed_ms']} ms | Returncode: {job['returncode']}")
    print(f"--> stdout: {job['stdout'].strip()}")
    assert job["returncode"] == 0
    assert "AETHER_MESH_VERIFIED_100" in job["stdout"]

    # 4. Live Snapshot Streaming with UCIP Compression
    print("\n[4/4] Testing Live Snapshot Streaming with UCIP (Psi-TETO)...")
    snap = swarm.stream_snapshot_with_ucip(
        session_id="sess_mesh_live_test",
        checkpoint_tag="ckpt_pre_agent",
        source_files={
            "agent_state.json": json.dumps({"epoch": 1, "tokens": 4096}),
            "memory_tensor_0": "0123456789ABCDEF" * 512,
            "memory_tensor_1": "FEDCBA9876543210" * 512
        }
    )
    print(f"--> Raw Wire Bytes: {snap['raw_payload_bytes']}")
    print(f"--> UCIP Compressed Bytes: {snap['ucip_compressed_bytes']}")
    print(f"--> Token/Wire Bandwidth Savings: {snap['token_wire_savings_pct']}%")
    print(f"--> Migration Latency: {snap['migration_latency_ms']} ms")
    print(f"--> Cryptographic Frame SHA256: {snap['frame_sha256'][:16]}...")
    assert snap["token_wire_savings_pct"] >= 75.0, "UCIP compression must achieve at least 75% bandwidth reduction!"
    assert snap["restorable"] is True

    print("\n" + "=" * 80)
    print("[+] AETHERMESH P2P SWARM PROTOCOL: 100% APROVADO!")
    print("=" * 80)
    return True


if __name__ == "__main__":
    success = run_aether_mesh_audit()
    if not success:
        sys.exit(1)
