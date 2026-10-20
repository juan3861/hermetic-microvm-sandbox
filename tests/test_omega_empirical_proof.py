"""
TITAN-HYPERION OMEGA — Strict Empirical Proof & Verification Suite
==================================================================
Validates all 2 Gears (Cloud-Cascade 5 Tiers + Local-Core bwrap/RAM/MFT)
and all 7 Quantum-Mathematical Organs from github.com/juan3861 + Repository Compiler v2.0.
Designed for execution under AetherMind_Strict_Auditor.py (Zero Smoke Tolerance).
"""

import os
import sys
import json
import xml.etree.ElementTree as ET

HYPERION_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HYPERION_ROOT not in sys.path:
    sys.path.insert(0, HYPERION_ROOT)

from orchestrator import TitanHyperionOrchestrator


def run_strict_empirical_verification() -> None:
    print("=" * 80)
    print(" [TITAN-HYPERION OMEGA] INICIANDO PROVA EMPÍRICA DE PONTA A PONTA")
    print("=" * 80)

    orch = TitanHyperionOrchestrator()
    report = orch.execute_full_mission(
        repo_target=r"F:\UCIP",
        remote_git_url="https://github.com/juan3861/UCIP.git",
        primary_language="python"
    )

    # 1. Verify SOMA-NEXUS Thermodynamic Governance
    soma = report["soma_nexus_governance"]
    assert soma["initial_trust"] == "BLIND", f"Expected initial BLIND trust, got {soma['initial_trust']}"
    assert soma["final_trust"] == "PROVEN", f"Expected final PROVEN(4) trust, got {soma['final_trust']}"
    assert soma["final_trust_numeric"] == 4, f"Expected numeric trust 4, got {soma['final_trust_numeric']}"
    assert 0.0 < soma["salience"] < 1.0, f"Salience decay failed: {soma['salience']}"
    print(f"[PASS 1/5] SOMA-NEXUS Governor: BLIND(0) -> PROVEN(4) | Salience={soma['salience']} | Energy={soma['energy_remaining']}")

    # 2. Verify Gear 1: Cloud-Cascade (5 Free Cloud Tiers)
    cloud = report["gear_1_cloud_cascade"]
    assert cloud["cloud_cascade_ok"] is True, f"Cloud cascade failed: {cloud}"
    probes_by_tier = {p["tier"]: p for p in cloud["all_tier_probes"]}

    # Check Tier 1 (StackBlitz Wasm)
    t1 = probes_by_tier.get("TIER_1_STACKBLITZ_WASM", {})
    assert t1.get("ok") is True, f"Tier 1 StackBlitz failed: {t1}"

    # Check Tier 2 (CodeSandbox Firecracker MicroVM live sandbox_id)
    t2 = probes_by_tier.get("TIER_2_E2B_FIRECRACKER_MICROVM", {})
    assert t2.get("ok") is True and t2.get("sandbox_id"), f"Tier 2 MicroVM failed to return live sandbox_id: {t2}"

    # Check Tier 3 (juan3861/AetherMind_Cloud_Swarm 20-Node Matrix)
    t3 = probes_by_tier.get("TIER_3_AETHERMIND_SWARM_20X", {})
    assert t3.get("ok") is True and t3.get("parallel_vm_nodes") == 20, f"Tier 3 Cloud Swarm failed: {t3}"

    # Check Tier 5 (GitHub Codespaces fallback probe executed)
    t5 = probes_by_tier.get("TIER_5_GITHUB_CODESPACES", {})
    assert "tier" in t5, f"Tier 5 Codespaces probe missing: {t5}"
    print(
        f"[PASS 2/5] Engrenagem 1 (Cloud-Cascade): Live MicroVM ID={t2.get('sandbox_id')} "
        f"| StackBlitz=OK | Swarm=20 Nodes | Cascade Selected={cloud['selected_tier']} ({cloud['total_cascade_ms']} ms)"
    )

    # 3. Verify Gear 2: Local-Core (WSL2 bwrap + /dev/shm RAM Disk + fastmft Canary + .wsb)
    local_core = report["gear_2_local_core"]
    bwrap_local = local_core["local_ram_bwrap_jail"]
    assert bwrap_local["ok"] is True, f"Local bwrap RAM jail failed: {bwrap_local}"
    iso_proof = bwrap_local["isolation_proof"]
    assert iso_proof.get("windows_drives_unmounted") is True, f"/mnt was visible inside bwrap!: {iso_proof}"
    assert iso_proof.get("usr_readonly_enforced") is True, f"/usr was writable inside bwrap!: {iso_proof}"
    assert iso_proof.get("network_airgapped") is True, f"Network was not airgapped inside bwrap!: {iso_proof}"

    bwrap_remote = local_core["remote_virtualized_git_ram_clone"]
    assert bwrap_remote["ok"] is True, f"Remote virtualized git clone in /dev/shm failed: {bwrap_remote}"
    assert "REMOTE_RAM_CLONE_OK:" in bwrap_remote["stdout"], f"Missing remote clone marker: {bwrap_remote['stdout']}"

    canary = local_core["fastmft_forensic_canary"]
    assert canary["zero_host_mutation_proven"] is True, "Host directory was mutated during sandbox run!"
    assert canary["fastmft_native_active"] is True, "Compiled Go fastmft.exe did not execute!"

    wsb = local_core["windows_sandbox_wsb"]
    assert wsb["ok"] is True and os.path.isfile(wsb["wsb_path"]), f"Windows Sandbox .wsb missing: {wsb}"
    xml_root = ET.parse(wsb["wsb_path"]).getroot()
    assert xml_root.findtext("Networking") == "Disable", "WSB networking not disabled!"
    print(
        f"[PASS 3/5] Engrenagem 2 (Local-Core): bwrap Jail={bwrap_local['bwrap_jail_exec_ms']}ms "
        f"| Remote Git->RAM={bwrap_remote['ram_ingest_ms']}ms | Airgap/RO/Unmounted=True | fastmft Canary=PROVEN"
    )

    # 4. Verify Quantum-Mathematical Cortex (Hilbert/Grover, TensoLang SVD/MPS, UCIP, ARIA 7 Lenses, Phi-JIT x64)
    cortex = report["quantum_mathematical_cortex"]
    grover = cortex["fastmft_hilbert_grover"]
    assert abs(grover["hilbert_norm_verified"] - 1.0) < 1e-4, f"Hilbert state vector not normalized: {grover}"
    assert grover["shannon_entropy_bits"] > 0.0, f"Invalid Shannon entropy: {grover}"
    assert grover["grover_iterations_O_sqrt_N"] <= grover["classical_checks_O_N"], "Grover steps exceeded O(N)!"
    assert grover["fastmft_native_go_binary_verified"] is True, "Native Go fastmft.exe verification failed!"

    tenso = cortex["tensolang_svd_mps"]
    assert tenso["energy_retained_pct"] >= 95.0, f"SVD energy below 95%: {tenso}"
    assert tenso["svd_compression_ratio"] > 0.0, f"Invalid SVD ratio: {tenso}"

    telemetry = cortex["ucip_aria_phi_jit"]
    assert telemetry["ucip_token_savings_pct"] >= 50.0, f"UCIP savings below 50%: {telemetry}"
    assert telemetry["aria_7_lenses"]["verdict"] == "PASS", f"ARIA 7 lenses did not PASS: {telemetry['aria_7_lenses']}"
    assert telemetry["aria_7_lenses"]["score"] >= 0.75, f"ARIA score too low: {telemetry['aria_7_lenses']}"
    assert telemetry["phi_llvm_jit_x64"]["verified"] is True, f"Phi-LLVM-JIT x64 failed: {telemetry['phi_llvm_jit_x64']}"
    print(
        f"[PASS 4/5] Córtex Quântico-Matemático: Hilbert Norm={grover['hilbert_norm_verified']} "
        f"| Grover O(sqrt(N))={grover['grover_iterations_O_sqrt_N']} steps | SVD Energy={tenso['energy_retained_pct']}% "
        f"| UCIP Savings={telemetry['ucip_token_savings_pct']}% | ARIA={telemetry['aria_7_lenses']['score']} "
        f"| Phi-JIT x64={telemetry['phi_llvm_jit_x64']['exec_ms']}ms"
    )

    # 5. Verify Repository Compiler v2.0 Fusion (LibCST Slicer, Darwin/E-Graph/Z3, Bandit, Vulture, Radon, SBOM)
    rc_v2 = report["repository_compiler_v2_fusion"]
    assert "unused_dead_organ" in rc_v2["slicer"]["removed_dead_functions"], "LibCST Slicer failed to amputate dead organ!"
    assert rc_v2["darwin_egraph_z3"]["z3_symbolic_equivalence_proven"] is True, "Z3 equivalence failed!"
    assert rc_v2["darwin_egraph_z3"]["egraph_saturated_eclasses"] >= 2, "Quiche E-Graph saturation failed!"
    assert rc_v2["bandit_security"]["secure_capsule"] is True, "Bandit security check failed!"
    assert rc_v2["vulture_dead_code"]["zero_dead_code_certified"] is True, "Vulture dead code check failed!"
    assert rc_v2["radon_metrics"]["mi_rank"] == "A", f"Radon MI rank not A: {rc_v2['radon_metrics']}"
    assert "CycloneDX" in rc_v2["cyclonedx_sbom"]["bom_format"], "SBOM generation failed!"
    print(
        f"[PASS 5/5] Repository Compiler v2.0 Fusion: Slicer=OK | Z3=PROVEN | E-Classes={rc_v2['darwin_egraph_z3']['egraph_saturated_eclasses']} "
        f"| Bandit=SECURE | Vulture=0 Dead | Radon=Grade {rc_v2['radon_metrics']['mi_rank']} | SBOM={rc_v2['cyclonedx_sbom']['bom_format']}"
    )

    proof_file = os.path.join(HYPERION_ROOT, "hyperion_latest_proof.json")
    assert os.path.isfile(proof_file) and os.path.getsize(proof_file) > 500, "Proof JSON artifact not written!"
    print("=" * 80)
    print(f" [SUCESSO ABSOLUTO] TODAS AS 5 CAMADAS PROVADAS EM {report['total_mission_ms']} ms")
    print("=" * 80)


if __name__ == "__main__":
    run_strict_empirical_verification()
