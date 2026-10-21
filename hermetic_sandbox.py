"""
HERMETIC MICROVM SANDBOX — Universal Agent SDK Entry Point
==========================================================
Top-level import entry point enabling direct drop-in usage:
    from hermetic_sandbox import Sandbox, Process, CommandResult, StreamChunk, PTYSession, ReplayRecorder
"""

from sdk.hermetic_sandbox import (
    Sandbox,
    Process,
    CommandResult,
    SandboxFiles,
    SandboxCommands,
    ExecutionResult,
    REPLExecutionResult,
    StreamChunk,
    PTYSession,
    SandboxPTYManager,
    ReplayRecorder,
    ReplayEngine
)

__all__ = [
    "Sandbox",
    "Process",
    "CommandResult",
    "SandboxFiles",
    "SandboxCommands",
    "ExecutionResult",
    "REPLExecutionResult",
    "StreamChunk",
    "PTYSession",
    "SandboxPTYManager",
    "ReplayRecorder",
    "ReplayEngine"
]
__version__ = "2.4.0"
