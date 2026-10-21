"""
TITAN-HYPERION APEX — Interactive Pseudo-Terminal (PTY) Manager
===============================================================
Assimilates high-performance interactive terminal architecture from E2B, Modal, and Daytona:
  - Allocates real POSIX pseudo-terminals (openpty) inside volatile DDR RAM (/dev/shm)
  - Full bidirectional stdin / stdout streaming for interactive agent commands (e.g. bash, REPLs, ncurses)
  - Non-blocking I/O with millisecond latency via direct OS pipe bridge
  - Active Secret Sanitization on terminal stdout stream
  - Dynamic window resizing (winsize: cols, rows)
  - Zero host physical disk wear
"""

import os
import sys
import time
import uuid
import struct
import subprocess
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from security.secret_sanitizer import SecretSanitizer


class PTYSession:
    """
    Represents an active interactive pseudo-terminal session inside the MicroVM.
    Streams bidirectional I/O with millisecond latency and active secret sanitization.
    """

    def __init__(
        self,
        pty_id: str,
        session_id: str,
        ram_workspace: str,
        command: str = "sh",
        cols: int = 80,
        rows: int = 24
    ):
        self.pty_id = pty_id
        self.session_id = session_id
        self.ram_workspace = ram_workspace
        self.command = command
        self.cols = cols
        self.rows = rows
        self.sanitizer = SecretSanitizer()

        self._lock = threading.Lock()
        self._buffer = bytearray()
        self.closed: bool = False
        self._proc: Optional[subprocess.Popen] = None
        self._reader_thread: Optional[threading.Thread] = None

        self._start_pty()

    def _start_pty(self) -> None:
        """Launches the POSIX openpty bridge runner in the volatile RAM workspace."""
        runner_path = f"{self.ram_workspace}/runner_{self.pty_id}.py"
        init_cmd = f"mkdir -p '{self.ram_workspace}'"
        subprocess.run(["wsl.exe", "sh", "-c", init_cmd], capture_output=True, timeout=10)

        runner_code = f"""import os, sys, pty, select, termios, struct, fcntl

cols = {self.cols}
rows = {self.rows}
cmd = {repr(self.command)}
workspace = {repr(self.ram_workspace)}

try:
    os.makedirs(workspace, exist_ok=True)
    os.chdir(workspace)
except Exception:
    pass

master_fd, slave_fd = pty.openpty()
ws = struct.pack('HHHH', rows, cols, 0, 0)
fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, ws)

pid = os.fork()
if pid == 0:
    os.close(master_fd)
    os.setsid()
    fcntl.ioctl(slave_fd, termios.TIOCSCTTY, 0)
    for fd in (0, 1, 2):
        os.dup2(slave_fd, fd)
    if slave_fd > 2:
        os.close(slave_fd)
    os.environ['TERM'] = 'xterm-256color'
    os.environ['PAGER'] = 'cat'
    os.environ['PS1'] = '# '
    if cmd in ('sh', 'bash'):
        os.execlp('/bin/sh', 'sh')
    else:
        os.execlp('/bin/sh', 'sh', '-c', cmd)
    os._exit(1)

os.close(slave_fd)

# Signal ready
sys.stdout.buffer.write(b"PTY_READY\\n")
sys.stdout.buffer.flush()

fl = fcntl.fcntl(sys.stdin.fileno(), fcntl.F_GETFL)
fcntl.fcntl(sys.stdin.fileno(), fcntl.F_SETFL, fl | os.O_NONBLOCK)

while True:
    r, _, _ = select.select([master_fd, sys.stdin.fileno()], [], [], 0.05)
    if master_fd in r:
        try:
            data = os.read(master_fd, 4096)
            if not data:
                break
            sys.stdout.buffer.write(data)
            sys.stdout.buffer.flush()
        except OSError:
            break
    if sys.stdin.fileno() in r:
        try:
            in_data = sys.stdin.buffer.read(4096)
            if in_data:
                if b"__WINSIZE__:" in in_data:
                    lines = in_data.split(b"\\n")
                    for line in lines:
                        if line.startswith(b"__WINSIZE__:"):
                            parts = line.split(b":")
                            if len(parts) >= 3 and parts[1].isdigit() and parts[2].isdigit():
                                c, rw = int(parts[1]), int(parts[2])
                                ws_new = struct.pack('HHHH', rw, c, 0, 0)
                                fcntl.ioctl(master_fd, termios.TIOCSWINSZ, ws_new)
                        elif line:
                            os.write(master_fd, line + b"\\n")
                    continue
                os.write(master_fd, in_data)
        except OSError:
            pass
    wpid, status = os.waitpid(pid, os.WNOHANG)
    if wpid == pid:
        break
"""
        import base64
        b64 = base64.b64encode(runner_code.encode("utf-8")).decode("ascii")
        write_cmd = f"echo '{b64}' | base64 -d > '{runner_path}'"
        subprocess.run(["wsl.exe", "sh", "-c", write_cmd], capture_output=True, timeout=10)

        cmd_args = ["wsl.exe", "python3", "-u", runner_path]
        self._proc = subprocess.Popen(
            cmd_args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Start background reader thread immediately
        self._reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
        self._reader_thread.start()

        # Wait briefly for runner to be ready and clear handshake marker
        t_wait = time.perf_counter()
        while time.perf_counter() - t_wait < 3.0:
            with self._lock:
                if b"PTY_READY" in self._buffer:
                    eol = self._buffer.find(b"\n")
                    if eol != -1:
                        del self._buffer[:eol + 1]
                    else:
                        self._buffer.clear()
                    break
            time.sleep(0.02)

    def _reader_loop(self) -> None:
        """Reads chunks continuously from stdout pipe into the thread-safe buffer."""
        try:
            raw_stream = self._proc.stdout.raw if hasattr(self._proc.stdout, "raw") else self._proc.stdout
            while not self.closed and self._proc and raw_stream:
                chunk = raw_stream.read(4096)
                if not chunk:
                    break
                with self._lock:
                    self._buffer.extend(chunk)
        except Exception:
            pass

    def send_input(self, data: str) -> None:
        """Sends keystrokes or text commands to the running PTY stdin."""
        if self.closed or not self._proc or not self._proc.stdin:
            raise RuntimeError("Cannot send input to a closed PTYSession.")
        
        self._proc.stdin.write(data.encode("utf-8"))
        self._proc.stdin.flush()

    def read(self, timeout: float = 0.5) -> str:
        """
        Drains newly arrived output from the PTY, applies secret sanitization,
        and returns the decoded string.
        """
        if self.closed:
            return ""

        t0 = time.perf_counter()
        while time.perf_counter() - t0 <= timeout:
            with self._lock:
                if len(self._buffer) > 0:
                    raw_bytes = bytes(self._buffer)
                    self._buffer.clear()
                    raw_text = raw_bytes.decode("utf-8", errors="replace")
                    return self.sanitizer.sanitize(raw_text)
            time.sleep(0.02)

        with self._lock:
            raw_bytes = bytes(self._buffer)
            self._buffer.clear()
        raw_text = raw_bytes.decode("utf-8", errors="replace")
        return self.sanitizer.sanitize(raw_text)

    def resize(self, cols: int, rows: int) -> bool:
        """Dynamically adjusts the pseudo-terminal window geometry."""
        if self.closed or not self._proc or not self._proc.stdin:
            return False
        self.cols = cols
        self.rows = rows
        resize_msg = f"__WINSIZE__:{cols}:{rows}\n".encode("ascii")
        try:
            self._proc.stdin.write(resize_msg)
            self._proc.stdin.flush()
            return True
        except Exception:
            return False

    def is_alive(self) -> bool:
        """Checks if the PTY process is still running."""
        if self.closed or not self._proc:
            return False
        return self._proc.poll() is None

    def kill(self) -> bool:
        """Terminates the PTY session."""
        if self.closed:
            return True
        self.closed = True
        if self._proc:
            try:
                self._proc.kill()
                self._proc.wait(timeout=1.0)
            except Exception:
                pass
        return True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.kill()

    def __repr__(self) -> str:
        state = "ALIVE" if self.is_alive() else "CLOSED"
        return f"<PTYSession pty_id='{self.pty_id}' command='{self.command}' state='{state}'>"


class SandboxPTYManager:
    """
    Manages allocation, routing, and lifecycle of interactive PTY sessions
    confined to the volatile DDR RAM workspace.
    """

    def __init__(self, session_id: str, ram_workspace: str):
        self.session_id = session_id
        self.ram_workspace = ram_workspace
        self.sessions: Dict[str, PTYSession] = {}

    def create(
        self,
        command: str = "sh",
        cols: int = 80,
        rows: int = 24,
        pty_id: Optional[str] = None
    ) -> PTYSession:
        """Spawns an interactive pseudo-terminal session."""
        pid_str = pty_id or f"pty_{uuid.uuid4().hex[:8]}"
        session = PTYSession(
            pty_id=pid_str,
            session_id=self.session_id,
            ram_workspace=self.ram_workspace,
            command=command,
            cols=cols,
            rows=rows
        )
        self.sessions[pid_str] = session
        return session

    def get(self, pty_id: str) -> Optional[PTYSession]:
        return self.sessions.get(pty_id)

    def close_all(self) -> None:
        """Terminates all active PTY sessions."""
        for s in list(self.sessions.values()):
            s.kill()
        self.sessions.clear()


if __name__ == "__main__":
    mgr = SandboxPTYManager("test_pty_sess", "/dev/shm/test_pty_sess")
    print("[*] Creating PTY session...")
    pty = mgr.create("sh", cols=80, rows=24)
    print("PTY Created:", pty)
    
    pty.send_input("echo 'PTY_INTERACTIVE_OK'\n")
    time.sleep(0.3)
    out = pty.read(timeout=1.0)
    print("PTY Output received:", repr(out))
    assert "PTY_INTERACTIVE_OK" in out
    
    pty.send_input("echo 'SECRET_TEST: sk-proj-12345678901234567890'\n")
    time.sleep(0.3)
    secret_out = pty.read(timeout=1.0)
    print("Sanitized PTY Output:", repr(secret_out))
    assert "sk-***[REDACTED_OPENAI_KEY]***" in secret_out
    
    pty.kill()
    print("[+] PTY verification successful!")
