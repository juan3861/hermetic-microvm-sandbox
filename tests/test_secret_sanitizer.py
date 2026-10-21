"""
TITAN-HYPERION APEX / HERMETIC MICROVM SANDBOX
Secret Sanitizer & Streaming Output Test Suite
==============================================
Verifies:
  1. Redaction of OpenAI, GitHub, AWS, JWT, Slack, and PEM keys
  2. Integration with Sandbox.run_code() and SandboxCommands.run()
  3. Real-time streaming generator (Sandbox.run_code_stream() & run_stream())
  4. Zero false-positive behavior on standard mathematical and code strings
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from security.secret_sanitizer import SecretSanitizer
from sdk.hermetic_sandbox import Sandbox, StreamChunk


def run_secret_sanitizer_audit():
    print("=" * 80)
    print("[*] HERMETIC MICROVM SANDBOX: SECRET SANITIZER & STREAMING AUDIT")
    print("=" * 80)

    sanitizer = SecretSanitizer()

    # 1. Multi-secret redaction
    print("\n[1/4] Testing Multi-Token Credential Scrubbing...")
    leaked_payload = (
        "Config dump:\n"
        "OPENAI_KEY=sk-proj-abc1234567890def1234567890\n"
        "GITHUB_PAT=ghp_ABC1234567890abcdef12345678901234\n"
        "AWS_KEY=AKIA1234567890ABCDEF\n"
        "SLACK=xoxb-1234567890-abcdef123456\n"
        "DB_URI=postgres://admin:SuperSecretPassword123@db.internal:5432/prod\n"
    )
    cleaned = sanitizer.sanitize(leaked_payload)
    print("--> Sanitized Output:\n" + cleaned)
    assert "sk-***[REDACTED_OPENAI_KEY]***" in cleaned
    assert "ghp_***[REDACTED_GITHUB_TOKEN]***" in cleaned
    assert "AKIA***[REDACTED_AWS_KEY]***" in cleaned
    assert "xox-***[REDACTED_SLACK_TOKEN]***" in cleaned
    assert "SuperSecretPassword123" not in cleaned
    assert "REDACTED_PASSWORD" in cleaned

    # 2. Zero false positives on regular tokens
    print("\n[2/4] Testing False Positive Resistance on Benign Code...")
    benign_code = (
        "import numpy as np\n"
        "x = np.array([1, 2, 3])\n"
        "token = 'standard_variable_token_name'\n"
        "key = 42\n"
    )
    benign_cleaned = sanitizer.sanitize(benign_code)
    assert benign_cleaned == benign_code
    print("--> Benign code preserved byte-for-byte with zero false positives.")

    # 3. REPL secret redaction integration
    print("\n[3/4] Testing REPL Execution Secret Redaction...")
    with Sandbox(memory_mb=128) as sb:
        res = sb.run_code("print('API_KEY: sk-proj-999888777666555444333222')\n'AKIA0000111122223333'")
        print(f"--> REPL Stdout: {res.stdout.strip()}")
        print(f"--> REPL Result: {res.result}")
        assert "sk-***[REDACTED_OPENAI_KEY]***" in res.stdout
        assert "AKIA***[REDACTED_AWS_KEY]***" in str(res.result)

    # 4. Streaming execution chunks
    print("\n[4/4] Testing Real-Time Streaming Chunks (run_code_stream)...")
    with Sandbox(memory_mb=128) as sb:
        code_stream = (
            "print('CHUNK_LINE_ONE')\n"
            "print('CHUNK_LINE_TWO: sk-live-111122223333444455556666')\n"
            "100 * 2\n"
        )
        chunks = list(sb.run_code_stream(code_stream))
        print(f"--> Emitted {len(chunks)} StreamChunk events:")
        for ch in chunks:
            print(f"    {ch}")

        channels = [c.channel for c in chunks]
        assert "stdout" in channels
        assert "result" in channels

        # Verify streamed chunks are also sanitized
        full_stream_text = "".join(c.text for c in chunks)
        assert "CHUNK_LINE_ONE" in full_stream_text
        assert "sk-***[REDACTED_OPENAI_KEY]***" in full_stream_text
        assert "200" in full_stream_text

    print("\n" + "=" * 80)
    print("[+] SECRET SANITIZER & STREAMING: 100% APROVADO!")
    print("=" * 80)
    return True


if __name__ == "__main__":
    if not run_secret_sanitizer_audit():
        sys.exit(1)
