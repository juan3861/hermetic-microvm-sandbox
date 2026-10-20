"""
SOMA-NEXUS Thermodynamic Governor for TITAN-HYPERION OMEGA.
Integrates juan3861/soma-nexus (80 cognitive types, CogTrust 0..4, CogPhase,
Salience Decay S_{t+1} = gamma * S_t, and Energy Budgets) to govern sandbox
routing, network isolation, and formal trust promotion.
"""

import os
import sys
import time
from dataclasses import dataclass, field
from enum import IntEnum, Enum
from typing import Dict, Any, List, Optional

# Wire upstream juan3861/soma-nexus if cloned
_SOMA_DIR = r"F:\TITAN_HYPERION_OMEGA\upstream_arsenal\soma-nexus"
if os.path.isdir(_SOMA_DIR) and _SOMA_DIR not in sys.path:
    sys.path.insert(0, _SOMA_DIR)


class SandboxTrustLevel(IntEnum):
    """AXIOMA §01 TrustType hierarchy from juan3861/soma-nexus."""
    BLIND = 0      # Untrusted external code: MUST run with --unshare-all (zero network, RO root)
    WORKING = 1    # Cloned & syntax-checked inside ephemeral RAM Disk (/dev/shm)
    SEMANTIC = 2   # Sliced via LibCST/NetworkX & compressed via TensoLang SVD/MPS
    TRUSTED = 3    # Passed Bandit AST security, Vulture dead-code, and Radon MI Grade A
    PROVEN = 4     # Formally verified by Clingo ASP + Z3 SMT + ARIA 7 Lenses + Hermetic Execution


class SandboxExecutionPhase(Enum):
    """AXIOMA §28 PolicyCode execution regimes from juan3861/soma-nexus."""
    REFLEX = "reflex"       # <10ms boot (bwrap in /dev/shm or StackBlitz Wasm)
    ANALYTIC = "analytic"   # <1s (LibCST Slicing + TensoLang SVD + Clingo/Z3)
    FORENSIC = "forensic"   # <60s (Full batch oracle + fastmft USN Journal delta)
    AGENTIC = "agentic"     # Autonomous multi-repo swarm orchestration (20-node GitHub Actions)


@dataclass
class CognitiveSandboxState:
    """
    Thermodynamic state vector carried by every repository inside TITAN-HYPERION OMEGA.
    Follows the LTI state update and SOMA-NEXUS decay laws:
        S_{t+1} = gamma * S_t
        E_{t+1} = E_t - delta_E
    """
    target_id: str
    source_uri: str
    trust: SandboxTrustLevel = SandboxTrustLevel.BLIND
    phase: SandboxExecutionPhase = SandboxExecutionPhase.REFLEX
    salience: float = 1.0
    decay: float = 0.99
    energy_budget: float = 1.0
    created_at: float = field(default_factory=time.time)
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)

    def tick(self, energy_cost: float = 0.05) -> None:
        """Applies thermodynamic salience decay and deducts cognitive energy."""
        self.salience = round(self.salience * self.decay, 6)
        self.energy_budget = round(max(0.0, self.energy_budget - energy_cost), 6)

    @property
    def requires_airgap_network(self) -> bool:
        """Hard Invariant: Any code below TRUSTED (3) is strictly forbidden from network access."""
        return self.trust < SandboxTrustLevel.TRUSTED

    @property
    def requires_readonly_host_mounts(self) -> bool:
        """Hard Invariant: Host filesystem must be mounted strictly Read-Only (--ro-bind)."""
        return self.trust <= SandboxTrustLevel.PROVEN

    def record_transition(
        self,
        new_trust: SandboxTrustLevel,
        new_phase: SandboxExecutionPhase,
        proof_summary: str,
        metrics: Optional[Dict[str, Any]] = None
    ) -> None:
        prev_trust = self.trust
        prev_phase = self.phase
        self.trust = new_trust
        self.phase = new_phase
        self.tick(energy_cost=0.08)
        self.audit_trail.append({
            "timestamp": time.time(),
            "from_trust": prev_trust.name,
            "to_trust": new_trust.name,
            "from_phase": prev_phase.value,
            "to_phase": new_phase.value,
            "salience": self.salience,
            "energy_remaining": self.energy_budget,
            "proof_summary": proof_summary,
            "metrics": metrics or {}
        })


class SomaThermodynamicGovernor:
    """
    Autonomous AGI Decision Router for TITAN-HYPERION OMEGA.
    Evaluates repository topology, privacy constraints, and cloud availability to select
    between Gear 1 (Cloud-Cascade 5 Tiers) and Gear 2 (Local-Core Kernel/RAM/MFT).
    """

    def __init__(self):
        self.upstream_soma_loaded = False
        try:
            import types as soma_types  # type: ignore
            if hasattr(soma_types, "CogTrust") and hasattr(soma_types, "CogMeta"):
                self.upstream_soma_loaded = True
        except Exception:
            pass

    def initialize_state(self, target_id: str, source_uri: str) -> CognitiveSandboxState:
        state = CognitiveSandboxState(
            target_id=target_id,
            source_uri=source_uri,
            trust=SandboxTrustLevel.BLIND,
            phase=SandboxExecutionPhase.REFLEX,
            salience=1.0,
            energy_budget=1.0
        )
        state.audit_trail.append({
            "timestamp": time.time(),
            "event": "INIT_SOMA_STATE",
            "trust": state.trust.name,
            "phase": state.phase.value,
            "airgap_enforced": state.requires_airgap_network,
            "upstream_soma_nexus_linked": self.upstream_soma_loaded
        })
        return state

    def select_execution_strategy(
        self,
        state: CognitiveSandboxState,
        primary_language: str = "python",
        is_private: bool = False,
        prefer_local_kernel: bool = False,
        batch_size: int = 1,
        network_online: bool = True
    ) -> Dict[str, Any]:
        """
        Determines the optimal execution gear and fallback ladder.
        """
        lang = primary_language.lower().strip()

        # Rule 1: If private repo, offline, or explicit local kernel enforcement -> Gear 2 (Local-Core)
        if is_private or not network_online or prefer_local_kernel or state.requires_airgap_network:
            primary_gear = "GEAR_2_LOCAL_CORE"
        else:
            primary_gear = "GEAR_1_CLOUD_CASCADE"

        # Construct the 5-Tier Cloud Cascade order tailored to language & batch size
        if batch_size >= 5:
            cloud_ladder = [
                "TIER_3_AETHERMIND_SWARM_20X",
                "TIER_2_E2B_FIRECRACKER_MICROVM",
                "TIER_4_DAYTONA_MODAL_RUST",
                "TIER_1_STACKBLITZ_WASM",
                "TIER_5_GITHUB_CODESPACES"
            ]
        elif lang in ("javascript", "typescript", "node", "react", "vue", "nextjs"):
            cloud_ladder = [
                "TIER_1_STACKBLITZ_WASM",
                "TIER_2_E2B_FIRECRACKER_MICROVM",
                "TIER_3_AETHERMIND_SWARM_20X",
                "TIER_4_DAYTONA_MODAL_RUST",
                "TIER_5_GITHUB_CODESPACES"
            ]
        else:
            cloud_ladder = [
                "TIER_2_E2B_FIRECRACKER_MICROVM",
                "TIER_3_AETHERMIND_SWARM_20X",
                "TIER_4_DAYTONA_MODAL_RUST",
                "TIER_1_STACKBLITZ_WASM",
                "TIER_5_GITHUB_CODESPACES"
            ]

        local_ladder = [
            "LOCAL_T1_WSL2_BWRAP_RAMDISK",
            "LOCAL_T2_WINDOWS_SANDBOX_WSB",
            "LOCAL_T3_SANITIZED_NAMESPACE_SUBPROCESS"
        ]

        return {
            "target_id": state.target_id,
            "primary_gear": primary_gear,
            "trust_level": state.trust.name,
            "airgap_network_required": state.requires_airgap_network,
            "readonly_mounts_required": state.requires_readonly_host_mounts,
            "cloud_cascade_ladder": cloud_ladder,
            "local_core_ladder": local_ladder,
            "soma_nexus_active": True
        }
