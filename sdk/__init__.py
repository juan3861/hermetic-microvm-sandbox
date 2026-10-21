"""
HERMETIC MICROVM SANDBOX — Universal Agent SDK
==============================================
Drop-in high-performance replacement for E2B (e2b-dev), Docker, and Modal.
Allows AI agents (OpenHands, SWE-bench, AutoGen, CrewAI, LangChain)
to execute code in isolated, zero-wear volatile DDR RAM sandboxes with
microsecond latency and zero cloud costs.
"""

from .hermetic_sandbox import Sandbox, Process, CommandResult, SandboxFiles, SandboxCommands

__all__ = ["Sandbox", "Process", "CommandResult", "SandboxFiles", "SandboxCommands"]
__version__ = "2.1.0"
