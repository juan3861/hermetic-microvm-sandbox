# Hyperion Agent Sandbox: Security Architecture & Threat Model

## 1. Adversarial Threat Model

Hyperion is engineered under the assumption that all executed code is **actively hostile and adversarial**. This includes:
- Remote code execution payloads designed to escape containers.
- Fork-bombs attempting to exhaust host process tables.
- Memory allocation bombs attempting to trigger Host OS OOM killers.
- Reverse shells attempting to connect back to Command & Control (C2) servers.
- Filesystem traversal exploits searching for sensitive host drives (`C:\`, SSH keys, credentials).

---

## 2. The 6-Vector Red-Team Penetration Suite

Hyperion includes a built-in adversarial testing harness ([`security/adversarial_redteam.py`](file:///F:/TITAN_HYPERION_OMEGA/security/adversarial_redteam.py)) that validates containment against 6 catastrophic attack vectors:

| Attack Vector | Payload Mechanism | Containment Layer | Test Verdict |
| :--- | :--- | :--- | :--- |
| **1. Host Filesystem Escape** | Probing `/mnt/c`, `/mnt/f`, `/host`, `/etc/shadow` | Hermetic mount table (`bwrap` cloaking) | **NEUTRALIZED** |
| **2. Network Egress Leak** | Socket connection to external DNS `8.8.8.8:53` | Hard airgap (`--unshare-all`, zero loopback) | **NEUTRALIZED** |
| **3. Fork-Bomb Denial of Service** | Bash recursive fork bomb `:(){ :\|:& };:` | Process table hard-limit & timeout killer | **NEUTRALIZED** |
| **4. RAM Exhaustion Bomb** | Memory allocation spike ($10^9$ ints) | Kernel tmpfs memory budget | **NEUTRALIZED** |
| **5. Infinite CPU Hang** | Tight busy-wait loop `while True: pass` | Hardware CPU timer kill (exit code 124) | **NEUTRALIZED** |
| **6. Host MFT Mutation** | Silent background file modifications | `fastmft.exe` USN Journal Canary check | **NEUTRALIZED** |

### Empirical Red-Team Suite Output
```json
{
  "suite": "TITAN-HYPERION APEX RED-TEAM ARMOR SUITE",
  "all_attacks_neutralized": true,
  "containment_score_pct": 100.0,
  "attacks_executed": 6,
  "attacks_neutralized": 6
}
```

---

## 3. Defense-in-Depth Mechanics

1. **Airgap Enforcement**:
   When `--unshare-all` is passed to Bubblewrap, the Linux kernel isolates the network namespace (`CLONE_NEWNET`). The sandbox process sees no network interfaces, no loopback interface, and cannot create raw or stream sockets.
2. **Read-Only Host Mounts**:
   System binaries (`/usr`, `/bin`, `/lib`, `/lib64`) are mounted `--ro-bind`. Any attempted write operation fails immediately with `EROFS` (Read-only file system).
3. **Host Storage Blindness**:
   Windows filesystem mount points (`/mnt/c`, `/mnt/f`, etc.) are explicitly excluded from the mount table. The untrusted process has no path resolution leading to the host storage.
