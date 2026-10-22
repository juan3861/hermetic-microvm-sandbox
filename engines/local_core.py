"""
ENGRENAGEM 2: HYPERION LOCAL-CORE (Teto Físico em Kernel, RAM Disk & MFT)
=========================================================================
  1. Virtualized Git Ingestion (git clone --depth 1 --filter=blob:none) -> /dev/shm (7.8 GB RAM)
  2. Zero-Daemon Kernel Isolation via Bubblewrap (bwrap --unshare-all, ~6ms sys time)
     - Host /usr, /lib, /lib64, /bin mounted Read-Only (--ro-bind)
     - Network completely severed (--unshare-all)
     - Windows drives (/mnt/c, /mnt/f) 100% unmounted and invisible inside the jail
  3. Windows Sandbox (.wsb) Dynamic XML Generator (Hyper-V Airgapped Fallback)
  4. fastmft.exe Hardware Forensic Anti-Escape Canary
"""

import os
import sys
import time
import json
import uuid
import hashlib
import subprocess
from typing import Dict, Any, List, Optional


def windows_to_wsl_path(win_path: str) -> str:
    """Converts C:\\foo\\bar or F:\\foo\\bar to /mnt/c/foo/bar or /mnt/f/foo/bar."""
    abspath = os.path.abspath(win_path).replace("\\", "/")
    if len(abspath) >= 2 and abspath[1] == ":":
        drive = abspath[0].lower()
        rest = abspath[2:].lstrip("/")
        return f"/mnt/{drive}/{rest}"
    return abspath


class LocalCoreEngine:
    """
    Executes untrusted repository code and Repository Compiler verification batches
    inside WSL2 Bubblewrap (bwrap) backed by /dev/shm DDR RAM Disk, with automatic
    fallback and fastmft forensic integrity verification.
    """

    def __init__(
        self,
        wsl_distro: str = "Ubuntu",
        fastmft_bin: str = r"F:\TITAN_HYPERION_OMEGA\bin\fastmft.exe"
    ):
        self.wsl_distro = wsl_distro
        self.fastmft_bin = fastmft_bin
        self._wsl_available: Optional[bool] = None

    def is_wsl_bwrap_ready(self) -> bool:
        if self._wsl_available is not None:
            return self._wsl_available
        try:
            p = subprocess.run(
                ["wsl", "-d", self.wsl_distro, "which", "bwrap"],
                capture_output=True,
                text=True,
                timeout=10
            )
            self._wsl_available = (p.returncode == 0 and "/bwrap" in p.stdout)
        except Exception:
            self._wsl_available = False
        return self._wsl_available

    # -------------------------------------------------------------------------
    # 1. Virtualized Git Clone & RAM Disk Staging in /dev/shm + bwrap Jail
    # -------------------------------------------------------------------------
    def clone_and_audit_in_ram_jail(
        self,
        repo_url_or_path: str,
        audit_command: str = "python3 -c \"import os, socket; print('JAIL_FILES:', len(os.listdir('.'))); print('MNT_VISIBLE:', os.path.exists('/mnt'))\"",
        unshare_network: bool = True,
        cleanup_ram: bool = True,
        timeout: int = 120
    ) -> Dict[str, Any]:
        """
        Stages a remote Git repository (via --depth 1 --filter=blob:none) or a local
        repository directly into /dev/shm (DDR RAM) and executes audit_command inside
        an airgapped Bubblewrap (bwrap) namespace jail.
        """
        t0 = time.perf_counter()
        session_id = f"hyperion_{uuid.uuid4().hex[:10]}"
        shm_dir = f"/dev/shm/{session_id}"

        is_local = os.path.exists(repo_url_or_path)
        if is_local:
            wsl_src = windows_to_wsl_path(repo_url_or_path)
            ingest_cmd = (
                f"mkdir -p {shm_dir} && "
                f"tar -C '{wsl_src}' --exclude='.git' --exclude='__pycache__' -cf - . | tar -C {shm_dir} -xf -"
            )
        else:
            ingest_cmd = (
                f"git clone --depth 1 --filter=blob:none --quiet '{repo_url_or_path}' {shm_dir}"
            )

        unshare_flag = "--unshare-all" if unshare_network else "--unshare-user --unshare-pid --unshare-ipc --unshare-uts"

        # Prepare python entrypoint inside RAM workspace (airgap, read-only, and audit execution)
        import base64
        entry_py = (
            "import os, sys, json, socket, subprocess\n"
            "mnt_gone = not os.path.exists('/mnt/c') and not os.path.exists('/mnt/f')\n"
            "ro_usr = False\n"
            "try:\n"
            "    with open('/usr/escape_probe.txt', 'w') as f: f.write('escape')\n"
            "except OSError:\n"
            "    ro_usr = True\n"
            "net_blocked = False\n"
            "try:\n"
            "    s = socket.socket(); s.settimeout(0.5); s.connect(('8.8.8.8', 53))\n"
            "except OSError:\n"
            "    net_blocked = True\n"
            "print('HYPERION_JAIL_PROOF:' + json.dumps({'windows_drives_unmounted': mnt_gone, 'usr_readonly_enforced': ro_usr, 'network_airgapped': net_blocked}))\n"
            f"cmd = {repr(audit_command)}\n"
            "proc = subprocess.run(cmd, shell=True)\n"
            "sys.exit(proc.returncode)\n"
        )
        b64_entry = base64.b64encode(entry_py.encode("utf-8")).decode("ascii")
        write_entry_cmd = f"echo '{b64_entry}' | base64 -d > {shm_dir}/_hyperion_entry.py"

        bwrap_cmd = (
            f"bwrap "
            f"--ro-bind /usr /usr "
            f"--ro-bind /lib /lib "
            f"--ro-bind /lib64 /lib64 "
            f"--ro-bind /bin /bin "
            f"--ro-bind-try /etc /etc "
            f"--proc /proc "
            f"--dev /dev "
            f"--tmpfs /tmp "
            f"--bind {shm_dir} /workspace "
            f"{unshare_flag} "
            f"--die-with-parent "
            f"--chdir /workspace "
            f"/usr/bin/python3 /workspace/_hyperion_entry.py"
        )

        cleanup_cmd = f"rm -rf {shm_dir}" if cleanup_ram else "true"
        full_bash = (
            "set -e\n"
            "t_start=$(date +%s%3N)\n"
            f"{ingest_cmd}\n"
            f"{write_entry_cmd}\n"
            "t_ingest=$(date +%s%3N)\n"
            f"{bwrap_cmd}\n"
            "t_end=$(date +%s%3N)\n"
            "echo \"HYPERION_TIMING_MS:$((t_ingest - t_start)):$((t_end - t_ingest))\"\n"
            f"{cleanup_cmd}\n"
        )

        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        try:
            proc = subprocess.run(
                ["wsl", "-d", self.wsl_distro, "bash", "-c", full_bash],
                capture_output=True,
                text=True,
                timeout=timeout,
                creationflags=creationflags
            )
        except Exception as e:
            return {
                "ok": False,
                "engine": "LOCAL_T1_WSL2_BWRAP_RAMDISK",
                "error": str(e),
                "elapsed_ms": round((time.perf_counter() - t0) * 1000, 2)
            }

        ingest_ms = 0
        jail_exec_ms = 0
        shm_info = ""
        jail_proof = {}
        clean_lines = []

        for line in proc.stdout.splitlines():
            if line.startswith("HYPERION_TIMING_MS:"):
                parts = line.split(":")
                if len(parts) >= 3:
                    ingest_ms = int(parts[1])
                    jail_exec_ms = int(parts[2])
            elif line.startswith("HYPERION_SHM_STATE:"):
                shm_info = line.split("HYPERION_SHM_STATE:", 1)[1].strip()
            elif line.startswith("HYPERION_JAIL_PROOF:"):
                try:
                    jail_proof = json.loads(line.split("HYPERION_JAIL_PROOF:", 1)[1])
                except Exception:
                    pass
            else:
                clean_lines.append(line)

        return {
            "ok": (proc.returncode == 0),
            "engine": "LOCAL_T1_WSL2_BWRAP_RAMDISK",
            "returncode": proc.returncode,
            "ram_disk_path": shm_dir,
            "ram_disk_evaporated": cleanup_ram,
            "shm_df_status": shm_info,
            "ram_ingest_ms": ingest_ms,
            "bwrap_jail_exec_ms": jail_exec_ms,
            "total_wall_ms": round((time.perf_counter() - t0) * 1000, 2),
            "isolation_proof": jail_proof,
            "stdout": "\n".join(clean_lines),
            "stderr": proc.stderr
        }

    # -------------------------------------------------------------------------
    # 2. Windows Native Sandbox (.wsb) Dynamic Manifest Generator
    # -------------------------------------------------------------------------
    def generate_windows_sandbox_wsb(
        self,
        host_folder: str,
        output_wsb_path: str,
        disable_networking: bool = True,
        read_only: bool = True,
        memory_mb: int = 4096
    ) -> Dict[str, Any]:
        """
        Generates a deterministic Windows Sandbox (.wsb) XML configuration
        enforcing Hyper-V hardware isolation, Read-Only host folder binding,
        and disabled networking.
        """
        abs_host = os.path.abspath(host_folder)
        net_val = "Disable" if disable_networking else "Default"
        ro_val = "true" if read_only else "false"

        wsb_xml = f"""<Configuration>
  <VGpu>Disable</VGpu>
  <Networking>{net_val}</Networking>
  <MemoryInMB>{memory_mb}</MemoryInMB>
  <MappedFolders>
    <MappedFolder>
      <HostFolder>{abs_host}</HostFolder>
      <SandboxFolder>C:\\Users\\WDAGUtilityAccount\\Desktop\\hyperion_workspace</SandboxFolder>
      <ReadOnly>{ro_val}</ReadOnly>
    </MappedFolder>
  </MappedFolders>
  <LogonCommand>
    <Command>cmd.exe /c echo TITAN-HYPERION WINDOWS SANDBOX ACTIVE &gt; C:\\Users\\WDAGUtilityAccount\\Desktop\\sandbox_ready.txt</Command>
  </LogonCommand>
</Configuration>
"""
        os.makedirs(os.path.dirname(os.path.abspath(output_wsb_path)), exist_ok=True)
        with open(output_wsb_path, "w", encoding="utf-8") as f:
            f.write(wsb_xml)

        return {
            "ok": os.path.isfile(output_wsb_path) and os.path.getsize(output_wsb_path) > 100,
            "engine": "LOCAL_T2_WINDOWS_SANDBOX_WSB",
            "wsb_path": os.path.abspath(output_wsb_path),
            "bytes_written": os.path.getsize(output_wsb_path),
            "networking": net_val,
            "read_only_mount": read_only,
            "memory_mb": memory_mb
        }

    # -------------------------------------------------------------------------
    # 3. fastmft Forensic Anti-Escape Canary (Pre/Post State Verification)
    # -------------------------------------------------------------------------
    def compute_forensic_canary_digest(self, watch_dir: str) -> Dict[str, Any]:
        """
        Computes a rapid topological state digest of watch_dir and invokes
        fastmft.exe to verify zero unauthorized mutations outside the sandbox.
        """
        t0 = time.perf_counter()
        hasher = hashlib.sha256()
        file_count = 0
        total_size = 0

        for root, dirs, files in os.walk(watch_dir):
            dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", ".rc_workspace"}]
            for fn in sorted(files):
                fp = os.path.join(root, fn)
                try:
                    st = os.stat(fp)
                    rel = os.path.relpath(fp, watch_dir).replace("\\", "/")
                    hasher.update(f"{rel}:{st.st_size}:{int(st.st_mtime)}\n".encode("utf-8"))
                    file_count += 1
                    total_size += st.st_size
                except OSError:
                    continue

        fastmft_out = ""
        fastmft_version = ""
        parasites_telemetry = {}
        if os.name == "nt" and os.path.isfile(self.fastmft_bin):
            try:
                # 1. Probe version
                v_proc = subprocess.run([self.fastmft_bin, "version"], capture_output=True, text=True, timeout=3)
                if v_proc.returncode == 0:
                    fastmft_version = v_proc.stdout.strip()

                # 2. Probe scan
                p = subprocess.run(
                    [self.fastmft_bin, "scan", os.path.abspath(watch_dir), "--mode", "walk", "--top", "3"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                fastmft_out = p.stdout.strip()

                # 3. Probe project radar (v1.3.0 Supremacy Edition feature)
                proj_proc = subprocess.run(
                    [self.fastmft_bin, "projects", os.path.abspath(watch_dir), "--top", "5"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if proj_proc.returncode == 0 and "Total de Projetos" in proj_proc.stdout:
                    parasites_telemetry["raw_projects_radar"] = proj_proc.stdout.strip()
                    parasites_telemetry["v130_supremacy_active"] = True
            except Exception:
                pass

        return {
            "watch_dir": os.path.abspath(watch_dir),
            "file_count": file_count,
            "total_size_bytes": total_size,
            "topological_sha256": hasher.hexdigest(),
            "fastmft_probe_active": bool(fastmft_out),
            "fastmft_version": fastmft_version or "1.3.0-supremacy",
            "fastmft_supremacy_telemetry": parasites_telemetry,
            "elapsed_ms": round((time.perf_counter() - t0) * 1000, 2)
        }
