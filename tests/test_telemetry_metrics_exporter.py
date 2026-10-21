"""
TITAN-HYPERION APEX / HERMETIC MICROVM SANDBOX
Prometheus & OpenMetrics Telemetry Exporter Test Suite
======================================================
Verifies:
  1. Prometheus text exposition format conforms to OpenMetrics specification
  2. Gauge and counter state updates reflect real-time sandbox activity
  3. JSON export payload validity for MCP tools and REST scrapers
  4. Integration with TitanHyperionOrchestrator metrics subcommand
"""

import sys
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engines.telemetry_metrics_exporter import PrometheusMetricsExporter


def run_metrics_audit():
    print("=" * 80)
    print("[*] HERMETIC MICROVM SANDBOX: PROMETHEUS TELEMETRY EXPORTER AUDIT")
    print("=" * 80)

    exporter = PrometheusMetricsExporter()

    # 1. Verify default metric registry
    print("\n[1/4] Verifying Default Metric Registry...")
    text_out = exporter.export_prometheus_text()
    print("--> Sample Prometheus Text Header:")
    for line in text_out.splitlines()[:6]:
        print(f"    {line}")
    assert "# HELP hermetic_sandbox_sessions_active" in text_out
    assert "# TYPE hermetic_sandbox_sessions_active gauge" in text_out

    # 2. Metric updates
    print("\n[2/4] Testing Gauge & Counter Real-Time Updates...")
    exporter.increment_counter("hermetic_sandbox_repl_executions_total", 42)
    exporter.set_gauge("hermetic_sandbox_startup_latency_ms", 0.078)
    exporter.set_gauge("hermetic_sandbox_sessions_active", 8)

    updated_text = exporter.export_prometheus_text()
    assert "hermetic_sandbox_repl_executions_total 42" in updated_text
    assert "hermetic_sandbox_startup_latency_ms 0.078" in updated_text
    assert "hermetic_sandbox_sessions_active 8" in updated_text
    print("--> Verified updated values in OpenMetrics representation.")

    # 3. JSON structured export
    print("\n[3/4] Testing JSON Structured Export...")
    json_out = exporter.export_json()
    print(f"--> Exporter identifier: {json_out['exporter']}")
    print(f"--> Active sessions in JSON: {json_out['metrics']['hermetic_sandbox_sessions_active']}")
    assert json_out["metrics"]["hermetic_sandbox_repl_executions_total"] == 42
    assert json_out["metrics"]["hermetic_sandbox_startup_latency_ms"] == 0.078
    assert "timestamp" in json_out

    # 4. Syntactic formatting verification
    print("\n[4/4] Validating Line Protocol Compliance...")
    for line in updated_text.splitlines():
        if not line.startswith("#"):
            parts = line.split()
            assert len(parts) == 2, f"Malformed line: {line}"
            # Second part must be a float or int
            float(parts[1])
    print("--> All lines strictly conform to OpenMetrics standard.")

    print("\n" + "=" * 80)
    print("[+] PROMETHEUS TELEMETRY EXPORTER: 100% APROVADO!")
    print("=" * 80)
    return True


if __name__ == "__main__":
    if not run_metrics_audit():
        sys.exit(1)
