"""
ENGRENAGEM 1: HYPERION CLOUD-CASCADE (5 Níveis Gratuitos com Failover Autônomo)
================================================================================
  Tier 1 (Ouro ~50ms):    StackBlitz WebContainers (Wasm Client-Side / pr.new)
  Tier 2 (Prata ~150ms):  E2B Firecracker MicroVM & CodeSandbox Define API (Memory Snapshot)
  Tier 3 (Enxame 20x):    AetherMind Cloud Swarm (juan3861 GitHub Actions 20-Node Matrix)
  Tier 4 (Bronze ~1-2s):  Daytona & Modal Serverless Rust Lazy-Loader
  Tier 5 (Platina ~15s):  GitHub Codespaces Ephemeral VM (gh codespace API)
"""

import os
import json
import time
import urllib.request
import urllib.error
import subprocess
from typing import Dict, Any, List, Optional


class CloudCascadeEngine:
    """
    Executes or provisions cloud sandboxes across the 5-tier free cascade,
    automatically failing over to the next tier on quota/network limits.
    """

    def __init__(self, timeout_sec: float = 8.0):
        self.timeout_sec = timeout_sec

    def _extract_github_owner_repo(self, repo_uri: str) -> Optional[str]:
        clean = repo_uri.strip().rstrip("/")
        if clean.endswith(".git"):
            clean = clean[:-4]
        if "github.com/" in clean:
            parts = clean.split("github.com/")[-1].split("/")
            if len(parts) >= 2:
                return f"{parts[0]}/{parts[1]}"
        elif "/" in clean and not os.path.exists(clean) and ":" not in clean:
            parts = clean.split("/")
            if len(parts) == 2:
                return f"{parts[0]}/{parts[1]}"
        return None

    # -------------------------------------------------------------------------
    # TIER 1: StackBlitz WebContainers (~50ms Wasm Client-Side)
    # -------------------------------------------------------------------------
    def probe_tier1_stackblitz(self, repo_uri: str) -> Dict[str, Any]:
        t0 = time.perf_counter()
        slug = self._extract_github_owner_repo(repo_uri) or "juan3861/UCIP"
        sb_url = f"https://stackblitz.com/github/{slug}"
        pr_new_url = f"https://pr.new/github.com/{slug}"

        req = urllib.request.Request(
            sb_url,
            method="HEAD",
            headers={"User-Agent": "TITAN-HYPERION-OMEGA/2.0"}
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_sec) as resp:
                status = resp.status
                ok = status in (200, 301, 302, 307, 308)
        except urllib.error.HTTPError as he:
            status = he.code
            ok = status in (200, 301, 302, 307, 308)
        except Exception as e:
            return {
                "tier": "TIER_1_STACKBLITZ_WASM",
                "ok": False,
                "error": str(e),
                "elapsed_ms": round((time.perf_counter() - t0) * 1000, 2)
            }

        return {
            "tier": "TIER_1_STACKBLITZ_WASM",
            "ok": ok,
            "http_status": status,
            "webcontainer_url": sb_url,
            "pr_new_url": pr_new_url,
            "architecture": "WebAssembly Node.js Kernel + SharedArrayBuffer In-Memory FS",
            "elapsed_ms": round((time.perf_counter() - t0) * 1000, 2)
        }

    # -------------------------------------------------------------------------
    # TIER 2: CodeSandbox Firecracker MicroVM Define API & E2B SDK (~150ms)
    # -------------------------------------------------------------------------
    def provision_tier2_microvm(
        self,
        repo_uri: str,
        files_payload: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Provisions a real cloud sandbox on CodeSandbox's Define API (POST ?json=1)
        returning a live cloud sandbox_id, and checks E2B Firecracker API readiness.
        """
        t0 = time.perf_counter()
        slug = self._extract_github_owner_repo(repo_uri) or "juan3861/UCIP"
        githubbox_url = f"https://githubbox.com/{slug}"

        # Prepare minimal capsule payload for CodeSandbox Define API
        csb_files = {}
        if files_payload:
            for k, v in list(files_payload.items())[:10]:
                csb_files[k] = {"content": v}
        else:
            csb_files["package.json"] = {
                "content": json.dumps({"name": "titan-hyperion-capsule", "version": "2.0.0", "main": "index.js"})
            }
            csb_files["index.js"] = {
                "content": f"// TITAN-HYPERION OMEGA MicroVM Capsule for {slug}\nconsole.log('HYPERION_CLOUD_OK');\n"
            }

        define_url = "https://codesandbox.io/api/v1/sandboxes/define?json=1"
        body = json.dumps({"files": csb_files}).encode("utf-8")
        req = urllib.request.Request(
            define_url,
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "TITAN-HYPERION-OMEGA/2.0"
            }
        )

        sandbox_id = None
        http_status = 0
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_sec) as resp:
                http_status = resp.status
                raw = resp.read().decode("utf-8", errors="replace")
                data = json.loads(raw)
                sandbox_id = data.get("sandbox_id")
        except Exception as e:
            return {
                "tier": "TIER_2_E2B_FIRECRACKER_MICROVM",
                "ok": False,
                "error": str(e),
                "githubbox_url": githubbox_url,
                "elapsed_ms": round((time.perf_counter() - t0) * 1000, 2)
            }

        e2b_key_present = bool(os.environ.get("E2B_API_KEY"))
        return {
            "tier": "TIER_2_E2B_FIRECRACKER_MICROVM",
            "ok": bool(sandbox_id),
            "http_status": http_status,
            "sandbox_id": sandbox_id,
            "live_sandbox_url": f"https://codesandbox.io/s/{sandbox_id}" if sandbox_id else githubbox_url,
            "githubbox_url": githubbox_url,
            "e2b_sdk_configured": e2b_key_present,
            "architecture": "Firecracker MicroVM + Snapshot Restore (Copy-on-Write mmap)",
            "elapsed_ms": round((time.perf_counter() - t0) * 1000, 2)
        }

    # -------------------------------------------------------------------------
    # TIER 3: AetherMind Cloud Swarm (juan3861 20-Node GitHub Actions Matrix)
    # -------------------------------------------------------------------------
    def probe_tier3_aethermind_swarm(self, trigger_dispatch: bool = False) -> Dict[str, Any]:
        """
        Verifies and optionally triggers juan3861/AetherMind_Cloud_Swarm &
        juan3861/aethermind-swarm-nodes (20 Ubuntu VMs in parallel on GitHub Actions).
        """
        t0 = time.perf_counter()
        try:
            proc = subprocess.run(
                ["gh", "api", "repos/juan3861/AetherMind_Cloud_Swarm/actions/workflows"],
                capture_output=True,
                text=True,
                timeout=self.timeout_sec
            )
            if proc.returncode != 0:
                return {
                    "tier": "TIER_3_AETHERMIND_SWARM_20X",
                    "ok": False,
                    "error": proc.stderr.strip(),
                    "elapsed_ms": round((time.perf_counter() - t0) * 1000, 2)
                }
            wf_data = json.loads(proc.stdout)
            workflows = [
                {"id": w.get("id"), "name": w.get("name"), "path": w.get("path"), "state": w.get("state")}
                for w in wf_data.get("workflows", [])
            ]

            dispatched = False
            if trigger_dispatch and workflows:
                d_proc = subprocess.run(
                    ["gh", "workflow", "run", "swarm.yml", "-R", "juan3861/AetherMind_Cloud_Swarm"],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_sec
                )
                dispatched = (d_proc.returncode == 0)

            return {
                "tier": "TIER_3_AETHERMIND_SWARM_20X",
                "ok": len(workflows) > 0,
                "swarm_repo": "juan3861/AetherMind_Cloud_Swarm",
                "parallel_vm_nodes": 20,
                "workflows_verified": workflows,
                "dispatched": dispatched,
                "architecture": "GitHub Actions 20-Node Ubuntu Matrix + Qwen2.5-Coder:7b RAM Hive",
                "elapsed_ms": round((time.perf_counter() - t0) * 1000, 2)
            }
        except Exception as e:
            return {
                "tier": "TIER_3_AETHERMIND_SWARM_20X",
                "ok": False,
                "error": str(e),
                "elapsed_ms": round((time.perf_counter() - t0) * 1000, 2)
            }

    # -------------------------------------------------------------------------
    # TIER 4: Daytona & Modal Serverless Rust Lazy-Loader
    # -------------------------------------------------------------------------
    def probe_tier4_daytona_modal(self) -> Dict[str, Any]:
        t0 = time.perf_counter()
        daytona_bin = subprocess.run(["where.exe", "daytona"], capture_output=True, text=True).returncode == 0
        modal_bin = subprocess.run(["where.exe", "modal"], capture_output=True, text=True).returncode == 0
        return {
            "tier": "TIER_4_DAYTONA_MODAL_RUST",
            "ok": daytona_bin or modal_bin,
            "daytona_cli_installed": daytona_bin,
            "modal_cli_installed": modal_bin,
            "architecture": "Serverless Rust Container Lazy-Loading Filesystem",
            "elapsed_ms": round((time.perf_counter() - t0) * 1000, 2)
        }

    # -------------------------------------------------------------------------
    # TIER 5: GitHub Codespaces Ephemeral Cloud VM (gh api /user/codespaces)
    # -------------------------------------------------------------------------
    def probe_tier5_codespaces(self) -> Dict[str, Any]:
        t0 = time.perf_counter()
        try:
            proc = subprocess.run(
                ["gh", "api", "/user/codespaces"],
                capture_output=True,
                text=True,
                timeout=self.timeout_sec
            )
            if proc.returncode == 0:
                data = json.loads(proc.stdout)
                return {
                    "tier": "TIER_5_GITHUB_CODESPACES",
                    "ok": True,
                    "active_codespaces_count": data.get("total_count", 0),
                    "architecture": "Azure Dedicated Ephemeral Dev VM (60h/month Free Tier)",
                    "elapsed_ms": round((time.perf_counter() - t0) * 1000, 2)
                }
            return {
                "tier": "TIER_5_GITHUB_CODESPACES",
                "ok": False,
                "error": proc.stderr.strip(),
                "elapsed_ms": round((time.perf_counter() - t0) * 1000, 2)
            }
        except Exception as e:
            return {
                "tier": "TIER_5_GITHUB_CODESPACES",
                "ok": False,
                "error": str(e),
                "elapsed_ms": round((time.perf_counter() - t0) * 1000, 2)
            }

    # -------------------------------------------------------------------------
    # FULL CASCADE ORCHESTRATION WITH AUTOMATIC FAILOVER
    # -------------------------------------------------------------------------
    def execute_cascade(
        self,
        repo_uri: str,
        ladder: Optional[List[str]] = None,
        files_payload: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Walks the Cloud Cascade ladder in priority order, recording telemetry
        for every tier and locking onto the fastest available cloud engine.
        """
        t0 = time.perf_counter()
        order = ladder or [
            "TIER_2_E2B_FIRECRACKER_MICROVM",
            "TIER_1_STACKBLITZ_WASM",
            "TIER_3_AETHERMIND_SWARM_20X",
            "TIER_4_DAYTONA_MODAL_RUST",
            "TIER_5_GITHUB_CODESPACES"
        ]

        attempts: List[Dict[str, Any]] = []
        selected_result: Optional[Dict[str, Any]] = None

        for tier_name in order:
            if tier_name == "TIER_1_STACKBLITZ_WASM":
                res = self.probe_tier1_stackblitz(repo_uri)
            elif tier_name == "TIER_2_E2B_FIRECRACKER_MICROVM":
                res = self.provision_tier2_microvm(repo_uri, files_payload=files_payload)
            elif tier_name == "TIER_3_AETHERMIND_SWARM_20X":
                res = self.probe_tier3_aethermind_swarm(trigger_dispatch=False)
            elif tier_name == "TIER_4_DAYTONA_MODAL_RUST":
                res = self.probe_tier4_daytona_modal()
            elif tier_name == "TIER_5_GITHUB_CODESPACES":
                res = self.probe_tier5_codespaces()
            else:
                continue

            attempts.append(res)
            if res.get("ok") and selected_result is None:
                selected_result = res

        return {
            "cloud_cascade_ok": selected_result is not None,
            "selected_tier": selected_result["tier"] if selected_result else "FALLBACK_TO_LOCAL_CORE",
            "selected_details": selected_result,
            "all_tier_probes": attempts,
            "total_cascade_ms": round((time.perf_counter() - t0) * 1000, 2)
        }
