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
    ReplayEngine,
    BranchManager,
    MemoryBranchDiff,
    ProvenanceAttestor,
    ExecutionProvenanceReceipt,
    BehavioralEBPFMonitor
)

HermeticSandbox = Sandbox

__all__ = [
    "Sandbox",
    "HermeticSandbox",
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
    "ReplayEngine",
    "BranchManager",
    "MemoryBranchDiff",
    "ProvenanceAttestor",
    "ExecutionProvenanceReceipt",
    "BehavioralEBPFMonitor"
]
__version__ = "2.6.0"
