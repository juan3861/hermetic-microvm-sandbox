"""
RC-v2 Sandbox Adapter: Drop-in Hermetic Execution Bridge for Repository Compiler v2.0.
Upgrades IndependentValidator._run_isolated_script and _run_isolated_batch to execute
inside WSL2 Bubblewrap (bwrap --unshare-all) backed by /dev/shm DDR RAM Disk.
"""

import os
import sys
from typing import Dict, Any

HYPERION_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HYPERION_ROOT not in sys.path:
    sys.path.insert(0, HYPERION_ROOT)

from engines.local_core import LocalCoreEngine


class HermeticValidatorBridge:
    """
    Provides a zero-leakage execution backend for Repository Compiler v2.0's
    IndependentValidator using TITAN-HYPERION OMEGA's LocalCoreEngine.
    """

    def __init__(self):
        self.local_engine = LocalCoreEngine()

    def run_workspace_script_in_bwrap_ram(
        self,
        workspace_dir: str,
        rel_script_path: str,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Copies workspace_dir into /dev/shm (DDR RAM) and executes rel_script_path
        inside an airgapped Bubblewrap (bwrap --unshare-all) Linux kernel namespace.
        """
        clean_rel = rel_script_path.replace("\\", "/").lstrip("/")
        res = self.local_engine.clone_and_audit_in_ram_jail(
            repo_url_or_path=workspace_dir,
            audit_command=f"PYTHONPATH=/workspace python3 '/workspace/{clean_rel}'",
            unshare_network=True,
            cleanup_ram=True,
            timeout=timeout
        )
        return {
            "returncode": res["returncode"],
            "stdout": res["stdout"],
            "stderr": res["stderr"],
            "bwrap_jail_exec_ms": res["bwrap_jail_exec_ms"],
            "isolation_proof": res["isolation_proof"]
        }
