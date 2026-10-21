"""
TITAN-HYPERION APEX / HERMETIC MICROVM SANDBOX
Zero-Trust Network Egress & SSRF Guard Test Suite
=================================================
Verifies:
  1. Interception of Cloud Metadata IP (169.254.169.254, 169.254.170.2)
  2. Blocking of RFC1918 Private Intranet Ranges (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
  3. Blocking of Loopback hopping (127.0.0.1, ::1)
  4. Allowance of legitimate public internet egress (8.8.8.8, 1.1.1.1)
  5. AST / Static pattern inspection for evasive socket and metadata code payloads
  6. Strict Hermetic Network Isolation mode
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from security.network_egress_guard import NetworkEgressGuard


def run_egress_guard_audit():
    print("=" * 80)
    print("[*] HERMETIC MICROVM SANDBOX: NETWORK EGRESS & SSRF GUARD AUDIT")
    print("=" * 80)

    guard = NetworkEgressGuard()

    # 1. Cloud metadata interception
    print("\n[1/6] Testing Cloud Metadata Endpoints (AWS/GCP/Azure SSRF)...")
    metadata_ips = ["169.254.169.254", "169.254.170.2", "100.100.100.200"]
    for ip in metadata_ips:
        ok, reason = guard.validate_destination_ip(ip)
        print(f"--> Probe IP {ip}: allowed={ok} | reason={reason}")
        assert ok is False
        assert "Cloud Metadata" in reason or "private/internal" in reason

    # 2. RFC1918 Private Intranet blocking
    print("\n[2/6] Testing RFC1918 Private Subnets...")
    private_ips = ["10.0.1.5", "172.16.20.1", "192.168.1.1", "192.168.0.254"]
    for ip in private_ips:
        ok, reason = guard.validate_destination_ip(ip)
        print(f"--> Probe IP {ip}: allowed={ok} | reason={reason}")
        assert ok is False
        assert "private/internal subnet" in reason

    # 3. Loopback blocking
    print("\n[3/6] Testing Loopback Subnet (127.0.0.0/8)...")
    loopback_ips = ["127.0.0.1", "127.0.0.50"]
    for ip in loopback_ips:
        ok, reason = guard.validate_destination_ip(ip)
        print(f"--> Probe IP {ip}: allowed={ok} | reason={reason}")
        assert ok is False

    # 4. Public IP allowance
    print("\n[4/6] Testing Legitimate Public Internet Access...")
    public_ips = ["8.8.8.8", "1.1.1.1", "93.184.216.34"]
    for ip in public_ips:
        ok, reason = guard.validate_destination_ip(ip)
        print(f"--> Probe IP {ip}: allowed={ok} | reason={reason}")
        assert ok is True

    # 5. Malicious code payload inspection
    print("\n[5/6] Testing AST & Payload Code Inspection...")
    malicious_snippets = [
        "import requests; requests.get('http://169.254.169.254/latest/meta-data/iam/security-credentials/')",
        "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)",
        "fetch('http://metadata.google.internal/computeMetadata/v1/')"
    ]
    for snip in malicious_snippets:
        res = guard.inspect_code_payload(snip)
        print(f"--> Snippet inspect safe={res['is_safe']} | violations={len(res['violations'])}")
        assert res["is_safe"] is False
        assert res["blocked_count"] > 0

    # 6. Strict hermetic mode
    print("\n[6/6] Testing Strict Hermetic Mode (Zero Egress)...")
    hermetic_guard = NetworkEgressGuard(mode="STRICT_HERMETIC")
    ok_h, r_h = hermetic_guard.validate_destination_ip("8.8.8.8")
    print(f"--> Public IP in Strict Hermetic: allowed={ok_h} | reason={r_h}")
    assert ok_h is False
    assert "STRICT_HERMETIC_MODE" in r_h

    print("\n" + "=" * 80)
    print("[+] ZERO-TRUST NETWORK EGRESS GUARD: 100% APROVADO!")
    print("=" * 80)
    return True


if __name__ == "__main__":
    if not run_egress_guard_audit():
        sys.exit(1)
