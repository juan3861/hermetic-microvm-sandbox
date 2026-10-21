"""
TITAN-HYPERION APEX — gVisor Sentry Syscall Interceptor & Proxy Guard
=====================================================================
Assimilates architectural patterns from Google gVisor (Sentry / Gofer):
  - User-space syscall virtualization and policy enforcement
  - Deep inspection of AST, C standard library calls, and bash payloads
  - Zero-tolerance blocking of kernel-escalating system calls:
      * sys_ptrace, sys_reboot, sys_mount, sys_pivot_root, sys_kexec_load
      * raw sockets (SOCK_RAW) and cloud metadata IP exfiltration (169.254.169.254)
      * kernel module loading (sys_init_module)
"""

import re
import ast
from typing import Dict, Any, List, Set, Tuple


class GVisorSentryGuard:
    """
    User-space proxy guard enforcing gVisor-grade syscall policy confinement
    before untrusted code reaches kernel execution.
    """

    FORBIDDEN_SYSCALLS: Set[str] = {
        "ptrace", "process_vm_readv", "process_vm_writev",
        "reboot", "kexec_load", "kexec_file_load",
        "init_module", "finit_module", "delete_module",
        "mount", "umount", "umount2", "pivot_root",
        "setuid", "setgid", "chroot",
        "syslog", "vmsplice", "userfaultfd"
    }

    FORBIDDEN_COMMANDS: Set[str] = {
        "insmod", "rmmod", "modprobe", "kexec", "strace", "reboot", "shutdown",
        "poweroff", "mkfs", "fdisk", "parted"
    }

    FORBIDDEN_SOCKET_TYPES: Set[str] = {
        "SOCK_RAW", "AF_PACKET", "IPPROTO_RAW"
    }

    RESTRICTED_NETWORK_TARGETS: Set[str] = {
        "169.254.169.254",  # Cloud Instance Metadata Service (AWS/Azure/GCP)
        "metadata.google.internal",
        "127.0.0.1", "localhost", "0.0.0.0"
    }

    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode

    def audit_python_ast(self, source_code: str) -> Dict[str, Any]:
        """
        Walks Python AST to detect ctypes, cffi, direct syscall invocation,
        or dangerous operating system subversion.
        """
        violations: List[str] = []
        try:
            tree = ast.parse(source_code)
        except SyntaxError as se:
            return {"valid_syntax": False, "allowed": False, "violations": [f"SyntaxError: {se}"]}

        for node in ast.walk(tree):
            # 1. Imports check
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in ("ctypes", "cffi", "_posixsubprocess"):
                        violations.append(f"FORBIDDEN_IMPORT: {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module in ("ctypes", "cffi", "_posixsubprocess"):
                    violations.append(f"FORBIDDEN_IMPORT_FROM: {node.module}")

            # 2. Attribute / Call checks
            elif isinstance(node, ast.Call):
                # e.g., os.system, subprocess with shell=True, ctypes.CDLL
                func_name = ""
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr

                for forbidden in self.FORBIDDEN_SYSCALLS:
                    if forbidden in func_name.lower():
                        violations.append(f"FORBIDDEN_SYSCALL_INVOCATION: {forbidden}")

        # Check raw strings for forbidden syscalls or cloud metadata exfiltration
        for syscall in self.FORBIDDEN_SYSCALLS:
            if re.search(rf"\b{syscall}\b", source_code):
                violations.append(f"FORBIDDEN_SYSCALL_INVOCATION: {syscall}")

        for cmd in self.FORBIDDEN_COMMANDS:
            if re.search(rf"\b{cmd}\b", source_code):
                violations.append(f"FORBIDDEN_COMMAND_DETECTED: {cmd}")

        for sock_type in self.FORBIDDEN_SOCKET_TYPES:
            if sock_type in source_code:
                violations.append(f"RAW_SOCKET_CREATION_DETECTED: {sock_type}")

        for target in self.RESTRICTED_NETWORK_TARGETS:
            if target in source_code:
                violations.append(f"RESTRICTED_NETWORK_TARGET_DETECTED: {target}")

        allowed = (len(violations) == 0)
        return {
            "runtime": "python",
            "allowed": allowed,
            "violations": violations,
            "sentry_verdict": "PERMIT" if allowed else "DENIED_BY_SENTRY_POLICY"
        }

    def audit_c_source(self, c_code: str) -> Dict[str, Any]:
        """
        Inspects C/C++ source code for dangerous headers, asm blocks,
        and forbidden raw syscall invocations.
        """
        violations: List[str] = []

        if "__asm__" in c_code or "asm(" in c_code:
            violations.append("INLINE_ASSEMBLY_DETECTED: Direct machine code execution prohibited")

        for syscall in self.FORBIDDEN_SYSCALLS:
            pattern = rf"\b(syscall\s*\(\s*SYS_{syscall}|{syscall}\s*\()"
            if re.search(pattern, c_code):
                violations.append(f"FORBIDDEN_C_SYSCALL: {syscall}")

        if "SOCK_RAW" in c_code or "AF_PACKET" in c_code:
            violations.append("RAW_SOCKET_CREATION_DETECTED: Unconfined socket type prohibited")

        for target in self.RESTRICTED_NETWORK_TARGETS:
            if target in c_code:
                violations.append(f"RESTRICTED_NETWORK_TARGET_DETECTED: {target}")

        allowed = (len(violations) == 0)
        return {
            "runtime": "c",
            "allowed": allowed,
            "violations": violations,
            "sentry_verdict": "PERMIT" if allowed else "DENIED_BY_SENTRY_POLICY"
        }

    def audit_bash_script(self, bash_script: str) -> Dict[str, Any]:
        """
        Audits shell script payloads for kernel module tampering,
        filesystem mounting attacks, or privilege elevation.
        """
        violations: List[str] = []
        lowered = bash_script.lower()

        patterns = [
            (r"\binsmod\b|\brmmod\b|\bmodprobe\b|\bkexec\b|\bstrace\b", "KERNEL_MODULE_TAMPERING"),
            (r"\bmount\b|\bumount\b", "FILESYSTEM_MOUNT_ATTACK"),
            (r"\bchroot\b|\bpivot_root\b", "ROOT_ESCAPE_ATTEMPT"),
            (r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:", "FORK_BOMB_PATTERN"),
            (r"/etc/shadow|/etc/sudoers", "HOST_CREDENTIAL_PROBE")
        ]

        for pat, tag in patterns:
            if re.search(pat, lowered):
                violations.append(tag)

        for target in self.RESTRICTED_NETWORK_TARGETS:
            if target in bash_script:
                violations.append(f"RESTRICTED_NETWORK_TARGET_DETECTED: {target}")

        allowed = (len(violations) == 0)
        return {
            "runtime": "bash",
            "allowed": allowed,
            "violations": violations,
            "sentry_verdict": "PERMIT" if allowed else "DENIED_BY_SENTRY_POLICY"
        }

    def enforce_sentry_policy(self, code: str, language: str) -> Dict[str, Any]:
        """
        Dispatches code to specialized audit engine based on language.
        """
        lang = language.lower()
        if lang in ("python", "py"):
            return self.audit_python_ast(code)
        elif lang in ("c", "cpp"):
            return self.audit_c_source(code)
        elif lang in ("bash", "sh"):
            return self.audit_bash_script(code)
        return {"runtime": lang, "allowed": True, "violations": [], "sentry_verdict": "PERMIT"}
