"""
HERMETIC MICROVM SANDBOX — Universal Agent SDK Entry Point
==========================================================
Top-level import entry point enabling direct drop-in usage:
    from hermetic_sandbox import Sandbox, Process, CommandResult
"""

from sdk.hermetic_sandbox import Sandbox, Process, CommandResult, SandboxFiles, SandboxCommands, ExecutionResult, REPLExecutionResult

__all__ = ["Sandbox", "Process", "CommandResult", "SandboxFiles", "SandboxCommands", "ExecutionResult", "REPLExecutionResult"]
__version__ = "2.2.0"
