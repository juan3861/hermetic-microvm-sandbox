"""
TITAN-HYPERION APEX — Model Context Protocol (MCP) Server
==========================================================
Exposes the Hyperion Sandbox and its Quantum-Mathematical Cortex as a standard
JSON-RPC 2.0 Model Context Protocol (MCP) server, allowing Claude Code, Devin,
Cursor, and autonomous AGI agents to natively spawn and control sandboxes.
"""

import sys
import json
import uuid
from typing import Dict, Any, List

from orchestrator import TitanHyperionOrchestrator


class HyperionMCPServer:
    """
    Standard MCP (Model Context Protocol) Server for TITAN-HYPERION APEX.
    """

    TOOLS_SCHEMA = [
        {
            "name": "hyperion_execute_code",
            "description": "Executes polyglot code (Python, JavaScript, C, Bash) in an airgapped, zero-wear DDR RAM sandbox (/dev/shm).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Source code to execute"},
                    "language": {"type": "string", "enum": ["python", "javascript", "c", "bash"], "description": "Language"}
                },
                "required": ["code"]
            }
        },
        {
            "name": "hyperion_time_travel_snapshot",
            "description": "Takes an instantaneous in-RAM Copy-on-Write (CoW) memory snapshot (Firecracker/CubeSandbox pattern).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "checkpoint_name": {"type": "string"}
                },
                "required": ["session_id", "checkpoint_name"]
            }
        },
        {
            "name": "hyperion_time_travel_rollback",
            "description": "Reverts the RAM workspace to a pristine checkpoint, discarding errors or destructive modifications.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "checkpoint_name": {"type": "string"}
                },
                "required": ["session_id", "checkpoint_name"]
            }
        },
        {
            "name": "hyperion_cartograph_codebase",
            "description": "Performs Quantum-Topological Cartography: TensoLang SVD, Shannon Entropy, and Grover O(sqrt(N)) search.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "target_dir": {"type": "string"},
                    "keywords": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["target_dir"]
            }
        },
        {
            "name": "hyperion_wasm_exec",
            "description": "Runs compiled WebAssembly modules in a microsecond capability sandbox (Wasmtime pattern).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "wat_or_wasm_hex": {"type": "string"},
                    "export_func_name": {"type": "string"},
                    "func_args": {"type": "array"}
                },
                "required": ["wat_or_wasm_hex", "export_func_name", "func_args"]
            }
        }
    ]

    def __init__(self):
        self.orchestrator = TitanHyperionOrchestrator()

    def handle_request(self, req: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes standard JSON-RPC 2.0 MCP requests.
        """
        req_id = req.get("id")
        method = req.get("method", "")
        params = req.get("params", {})

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "hyperion-agent-sandbox",
                        "version": "2.0.0"
                    }
                }
            }

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": self.TOOLS_SCHEMA}
            }

        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            try:
                result_data = self._dispatch_tool(tool_name, arguments)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result_data, indent=2)}
                        ]
                    }
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32000, "message": str(e)}
                }

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"}
        }

    def _dispatch_tool(self, name: str, args: Dict[str, Any]) -> Any:
        if name == "hyperion_execute_code":
            return self.orchestrator.execute_polyglot(
                code=args.get("code", ""),
                language=args.get("language", "python")
            )
        elif name == "hyperion_time_travel_snapshot":
            return self.orchestrator.time_travel.create_snapshot(
                session_id=args.get("session_id", ""),
                checkpoint_name=args.get("checkpoint_name", "checkpoint_0")
            )
        elif name == "hyperion_time_travel_rollback":
            return self.orchestrator.time_travel.rollback_to_snapshot(
                session_id=args.get("session_id", ""),
                checkpoint_name=args.get("checkpoint_name", "checkpoint_0")
            )
        elif name == "hyperion_cartograph_codebase":
            return self.orchestrator.cartograph_repository(
                target_dir=args.get("target_dir", ""),
                grover_keywords=args.get("keywords")
            )
        elif name == "hyperion_wasm_exec":
            return self.orchestrator.wasm_engine.execute_wasm_function(
                wat_or_wasm_hex=args.get("wat_or_wasm_hex", ""),
                export_func_name=args.get("export_func_name", "add"),
                func_args=args.get("func_args", [])
            )
        raise ValueError(f"Unknown tool: {name}")


def run_stdio_server():
    server = HyperionMCPServer()
    for line in sys.stdin:
        line_clean = line.strip()
        if not line_clean:
            continue
        try:
            req = json.loads(line_clean)
            resp = server.handle_request(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except json.JSONDecodeError:
            pass


if __name__ == "__main__":
    run_stdio_server()
