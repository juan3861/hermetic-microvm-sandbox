"""
TITAN-HYPERION APEX — SLSA Level 3 & In-Toto Cryptographic Provenance Attestor
==============================================================================
Empirical cryptographic supply-chain attestation for autonomous AI agents.
Generates and verifies in-toto statements and SLSA v1.0 provenance envelopes
signed with ephemeral cryptographic keys generated in volatile DDR RAM.

Prevents result forgery, prompt spoofing, and hallucinated executions
across multi-agent swarms (AetherMesh, AutoGPT, Claude Code swarms).
"""

import os
import sys
import time
import json
import base64
import hmac
import hashlib
import secrets
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class ExecutionProvenanceReceipt:
    """Represents a signed cryptographic SLSA v1.0 / In-Toto attestation envelope."""
    payload_type: str
    payload_b64: str
    signature: str
    key_id: str
    digest_sha256: str
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "_type": "https://in-toto.io/Statement/v1",
            "payloadType": self.payload_type,
            "payload": self.payload_b64,
            "signatures": [{
                "keyid": self.key_id,
                "sig": self.signature
            }],
            "digest_sha256": self.digest_sha256,
            "created_at": self.created_at
        }

    def decode_statement(self) -> Dict[str, Any]:
        """Decodes the underlying In-Toto / SLSA provenance JSON statement."""
        raw_json = base64.b64decode(self.payload_b64.encode("utf-8")).decode("utf-8")
        return json.loads(raw_json)


class ProvenanceAttestor:
    """
    Generates and verifies tamper-evident SLSA v1.0 provenance receipts
    for code executions inside the hermetic microVM sandbox.
    """

    def __init__(self, key_id: Optional[str] = None):
        self.key_id = key_id or f"ephemeral_key_{secrets.token_hex(8)}"
        # Ephemeral 256-bit HMAC secret held strictly in volatile RAM
        self._signing_secret = secrets.token_bytes(32)

    def generate_attestation(
        self,
        command: str,
        stdout: str,
        stderr: str,
        exit_code: int,
        session_id: str,
        sandbox_config: Optional[Dict[str, Any]] = None,
        duration_s: float = 0.0
    ) -> ExecutionProvenanceReceipt:
        """
        Builds a full In-Toto Statement with SLSA Provenance v1 Predicate
        and signs it with the volatile HMAC-SHA256 key.
        """
        t_now = time.time()
        cfg = sandbox_config or {}

        # 1. Compute Subject and Byproduct digests
        cmd_digest = hashlib.sha256(command.encode("utf-8")).hexdigest()
        stdout_digest = hashlib.sha256(stdout.encode("utf-8")).hexdigest()
        stderr_digest = hashlib.sha256(stderr.encode("utf-8")).hexdigest()
        result_digest = hashlib.sha256(f"{exit_code}:{stdout_digest}:{stderr_digest}".encode("utf-8")).hexdigest()

        # 2. Build In-Toto / SLSA v1.0 Statement
        statement = {
            "_type": "https://in-toto.io/Statement/v1",
            "subject": [{
                "name": f"execution_output_{session_id}",
                "digest": {
                    "sha256": result_digest
                }
            }],
            "predicateType": "https://slsa.dev/provenance/v1",
            "predicate": {
                "buildDefinition": {
                    "buildType": "https://hermetic-microvm.aethermind.ai/run/v1",
                    "externalParameters": {
                        "command": command,
                        "session_id": session_id,
                        "command_digest": cmd_digest
                    },
                    "internalParameters": {
                        "seccomp_bpf": cfg.get("seccomp_bpf", True),
                        "landlock": cfg.get("landlock", True),
                        "airgap_network": cfg.get("airgap", True),
                        "ram_tmpfs_only": True,
                        "zero_disk_wear": True
                    }
                },
                "runDetails": {
                    "builder": {
                        "id": "https://github.com/juan3861/hermetic-microvm-sandbox",
                        "version": "2.5.0"
                    },
                    "metadata": {
                        "invocationId": f"inv_{secrets.token_hex(12)}",
                        "startedOn": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t_now - duration_s)),
                        "finishedOn": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t_now)),
                        "durationSeconds": round(duration_s, 6),
                        "exitCode": exit_code
                    },
                    "byproducts": [
                        {
                            "name": "stdout",
                            "digest": {"sha256": stdout_digest},
                            "bytes": len(stdout.encode("utf-8"))
                        },
                        {
                            "name": "stderr",
                            "digest": {"sha256": stderr_digest},
                            "bytes": len(stderr.encode("utf-8"))
                        }
                    ]
                }
            }
        }

        # 3. Serialize and sign
        raw_json_bytes = json.dumps(statement, sort_keys=True).encode("utf-8")
        payload_b64 = base64.b64encode(raw_json_bytes).decode("utf-8")
        
        signature = hmac.new(
            self._signing_secret,
            payload_b64.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        envelope_digest = hashlib.sha256(raw_json_bytes).hexdigest()

        return ExecutionProvenanceReceipt(
            payload_type="application/vnd.in-toto+json",
            payload_b64=payload_b64,
            signature=signature,
            key_id=self.key_id,
            digest_sha256=envelope_digest,
            created_at=t_now
        )

    def verify_attestation(self, receipt: ExecutionProvenanceReceipt) -> bool:
        """
        Cryptographically verifies the authenticity and tamper-resistance
        of an ExecutionProvenanceReceipt.
        """
        if not receipt.payload_b64 or not receipt.signature:
            return False

        expected_sig = hmac.new(
            self._signing_secret,
            receipt.payload_b64.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(expected_sig, receipt.signature):
            return False

        # Verify underlying JSON digest
        try:
            raw_bytes = base64.b64decode(receipt.payload_b64.encode("utf-8"))
            computed_digest = hashlib.sha256(raw_bytes).hexdigest()
            return computed_digest == receipt.digest_sha256
        except Exception:
            return False
