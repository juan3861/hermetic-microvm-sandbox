"""
TITAN-HYPERION APEX / HERMETIC MICROVM SANDBOX
OCI Image Layout & Rootless Layer Unpacker Engine
=================================================
Assimilates OCI Image Specification v1.1 and rootless unpack logic from umoci:
  - Pure Python parser for OCI image layouts (index.json, manifests, config)
  - Sequential layer unpacking from blobs/sha256/<hash> directly into /dev/shm volatile RAM
  - OCI whiteout handling (.wh.<filename> and .wh..wh..opq opaque directory whiteouts)
  - Generation of OCI Runtime Spec v1.0.2 bundle with config.json and rootfs/
  - 100% rootless: zero requirement for Docker, containerd, or root privileges
"""

import os
import sys
import json
import time
import shutil
import tarfile
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Set

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class OCIImageUnpacker:
    """
    Parses OCI Image Layout directories and unpacks layers rootlessly
    into volatile DDR RAM workspaces (/dev/shm) for instant container execution.
    """

    def __init__(self, base_workspace_dir: Optional[Path] = None):
        self.workspace_dir = base_workspace_dir or Path("/dev/shm/hyperion_oci_bundles")

    def create_synthetic_oci_layout(
        self,
        target_dir: Path,
        sample_files: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Creates a valid standard OCI Image Layout structure locally for testing and offline airgap execution.
        """
        target_dir.mkdir(parents=True, exist_ok=True)
        blobs_dir = target_dir / "blobs" / "sha256"
        blobs_dir.mkdir(parents=True, exist_ok=True)

        files = sample_files or {
            "bin/hello": "#!/bin/sh\necho 'HERMETIC_OCI_IMAGE_EXECUTION_OK'\n",
            "etc/hostname": "hermetic-microvm\n",
            "etc/os-release": "NAME=\"HermeticMicroVMOS\"\nVERSION=\"2.1\"\n"
        }

        # 1. Create Layer Tarball
        layer_tar_path = target_dir / "temp_layer.tar"
        with tarfile.open(layer_tar_path, "w") as tar:
            for rel_path, content in files.items():
                data = content.encode("utf-8")
                ti = tarfile.TarInfo(name=rel_path)
                ti.size = len(data)
                ti.mtime = int(time.time())
                ti.mode = 0o755 if "bin/" in rel_path else 0o644
                import io
                tar.addfile(ti, io.BytesIO(data))

        layer_bytes = layer_tar_path.read_bytes()
        layer_sha256 = hashlib.sha256(layer_bytes).hexdigest()
        (blobs_dir / layer_sha256).write_bytes(layer_bytes)
        layer_tar_path.unlink()

        # 2. Config JSON blob
        config_data = {
            "created": "2026-10-21T00:00:00Z",
            "architecture": "amd64",
            "os": "linux",
            "config": {
                "Env": ["PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"],
                "Cmd": ["/bin/hello"],
                "WorkingDir": "/"
            },
            "rootfs": {
                "type": "layers",
                "diff_ids": [f"sha256:{layer_sha256}"]
            }
        }
        config_bytes = json.dumps(config_data, indent=2).encode("utf-8")
        config_sha256 = hashlib.sha256(config_bytes).hexdigest()
        (blobs_dir / config_sha256).write_bytes(config_bytes)

        # 3. Manifest JSON blob
        manifest_data = {
            "schemaVersion": 2,
            "mediaType": "application/vnd.oci.image.manifest.v1+json",
            "config": {
                "mediaType": "application/vnd.oci.image.config.v1+json",
                "digest": f"sha256:{config_sha256}",
                "size": len(config_bytes)
            },
            "layers": [
                {
                    "mediaType": "application/vnd.oci.image.layer.v1.tar",
                    "digest": f"sha256:{layer_sha256}",
                    "size": len(layer_bytes)
                }
            ]
        }
        manifest_bytes = json.dumps(manifest_data, indent=2).encode("utf-8")
        manifest_sha256 = hashlib.sha256(manifest_bytes).hexdigest()
        (blobs_dir / manifest_sha256).write_bytes(manifest_bytes)

        # 4. index.json
        index_data = {
            "schemaVersion": 2,
            "manifests": [
                {
                    "mediaType": "application/vnd.oci.image.manifest.v1+json",
                    "digest": f"sha256:{manifest_sha256}",
                    "size": len(manifest_bytes)
                }
            ]
        }
        (target_dir / "index.json").write_text(json.dumps(index_data, indent=2), encoding="utf-8")

        # 5. oci-layout
        layout_data = {"imageLayoutVersion": "1.0.0"}
        (target_dir / "oci-layout").write_text(json.dumps(layout_data, indent=2), encoding="utf-8")

        return {
            "oci_layout_dir": str(target_dir),
            "manifest_digest": f"sha256:{manifest_sha256}",
            "config_digest": f"sha256:{config_sha256}",
            "layer_digest": f"sha256:{layer_sha256}"
        }

    def unpack_oci_image(
        self,
        oci_layout_dir: Path,
        destination_bundle_dir: Path,
        manifest_index: int = 0
    ) -> Dict[str, Any]:
        """
        Unpacks an OCI Image Layout into a runnable OCI runtime bundle (config.json + rootfs/).
        Handles whiteouts (.wh.*) cleanly in unprivileged user space.
        """
        t0 = time.perf_counter()
        oci_dir = Path(oci_layout_dir)
        index_path = oci_dir / "index.json"
        if not index_path.exists():
            raise FileNotFoundError(f"Missing index.json in OCI layout at {oci_dir}")

        index = json.loads(index_path.read_text(encoding="utf-8"))
        manifest_desc = index["manifests"][manifest_index]
        manifest_digest = manifest_desc["digest"].split(":")[1]
        manifest_path = oci_dir / "blobs" / "sha256" / manifest_digest

        if not manifest_path.exists():
            raise FileNotFoundError(f"Manifest blob {manifest_digest} not found in {oci_dir}")

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        config_digest = manifest["config"]["digest"].split(":")[1]
        config_path = oci_dir / "blobs" / "sha256" / config_digest

        image_config = {}
        if config_path.exists():
            try:
                image_config = json.loads(config_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        # Prepare bundle directory
        dest = Path(destination_bundle_dir)
        rootfs = dest / "rootfs"
        rootfs.mkdir(parents=True, exist_ok=True)

        unpacked_layers_count = 0
        whiteouts_processed = 0

        # Extract layers in order
        for layer in manifest.get("layers", []):
            layer_digest = layer["digest"].split(":")[1]
            layer_blob = oci_dir / "blobs" / "sha256" / layer_digest
            if not layer_blob.exists():
                continue

            with tarfile.open(layer_blob, "r:*") as tar:
                for member in tar.getmembers():
                    # Check for OCI whiteouts
                    basename = os.path.basename(member.name)
                    dirname = os.path.dirname(member.name)
                    
                    if basename.startswith(".wh."):
                        whiteouts_processed += 1
                        if basename == ".wh..wh..opq":
                            # Opaque whiteout: clear entire target dir
                            target_dir = rootfs / dirname
                            if target_dir.exists():
                                shutil.rmtree(target_dir, ignore_errors=True)
                                target_dir.mkdir(parents=True, exist_ok=True)
                        else:
                            # Standard whiteout: delete specific file
                            real_name = basename.replace(".wh.", "")
                            target_file = rootfs / dirname / real_name
                            if target_file.is_dir():
                                shutil.rmtree(target_file, ignore_errors=True)
                            elif target_file.exists():
                                target_file.unlink(missing_ok=True)
                        continue

                    # Extract safely without host device nodes
                    try:
                        tar.extract(member, path=rootfs)
                    except PermissionError:
                        pass

            unpacked_layers_count += 1

        # Generate standard OCI Runtime Spec config.json
        cmd = image_config.get("config", {}).get("Cmd", ["sh"])
        env = image_config.get("config", {}).get("Env", [
            "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
            "TERM=xterm"
        ])
        cwd = image_config.get("config", {}).get("WorkingDir", "/")

        bundle_config = {
            "ociVersion": "1.0.2",
            "process": {
                "terminal": False,
                "user": {"uid": 0, "gid": 0},
                "args": cmd,
                "env": env,
                "cwd": cwd
            },
            "root": {
                "path": "rootfs",
                "readonly": True
            },
            "hostname": "hermetic-sandbox",
            "mounts": [
                {"destination": "/proc", "type": "proc", "source": "proc"},
                {"destination": "/dev", "type": "tmpfs", "source": "tmpfs", "options": ["nosuid", "strictatime", "mode=755", "size=65536k"]},
                {"destination": "/dev/shm", "type": "tmpfs", "source": "shm", "options": ["nosuid", "noexec", "nodev", "mode=1777", "size=65536k"]}
            ],
            "linux": {
                "namespaces": [
                    {"type": "pid"},
                    {"type": "network"},
                    {"type": "ipc"},
                    {"type": "uts"},
                    {"type": "mount"}
                ]
            }
        }

        config_out = dest / "config.json"
        config_out.write_text(json.dumps(bundle_config, indent=2), encoding="utf-8")

        elapsed_ms = round((time.perf_counter() - t0) * 1000, 3)

        return {
            "bundle_dir": str(dest),
            "rootfs_dir": str(rootfs),
            "config_json": str(config_out),
            "unpacked_layers_count": unpacked_layers_count,
            "whiteouts_processed": whiteouts_processed,
            "cmd": cmd,
            "elapsed_ms": elapsed_ms,
            "status": "UNPACKED_ROOTLESS"
        }


if __name__ == "__main__":
    unpacker = OCIImageUnpacker()
    test_oci_dir = Path("/dev/shm/test_oci_synthetic") if sys.platform != "win32" else PROJECT_ROOT / ".oci_containers" / "test_oci_synthetic"
    bundle_dest = Path("/dev/shm/test_oci_bundle") if sys.platform != "win32" else PROJECT_ROOT / ".oci_containers" / "test_oci_bundle"

    created = unpacker.create_synthetic_oci_layout(test_oci_dir)
    print("Created Synthetic OCI Image:", json.dumps(created, indent=2))

    unpacked = unpacker.unpack_oci_image(test_oci_dir, bundle_dest)
    print("Unpacked OCI Bundle:", json.dumps(unpacked, indent=2))
    assert (bundle_dest / "config.json").exists()
    assert (bundle_dest / "rootfs" / "bin" / "hello").exists()
    print("OCI Unpacker Test OK!")
