"""
GenesisLang Compiler — Full Pipeline
Tokenize → Parse → CodeGen → Execute
Usage:
    python compiler.py run file.gen        # Compile and run
    python compiler.py build file.gen      # Compile to Python
    python compiler.py build file.gen --js # Compile to JavaScript
    python compiler.py repl                # Interactive REPL
"""

import sys
import os
import subprocess
import tempfile
from pathlib import Path

from tokenizer import tokenize
from parser import parse, ParseError
from codegen import generate_python, generate_javascript


def compile_source(source, backend="python"):
    """Full pipeline: source string → Python/JS output."""
    tokens = tokenize(source)
    ast = parse(tokens)
    if backend == "python":
        return generate_python(ast)
    elif backend == "javascript":
        return generate_javascript(ast)
    else:
        raise ValueError(f"Unknown backend: {backend}")


def compile_file(path, backend="python"):
    """Compile a .gen file."""
    source = Path(path).read_text(encoding="utf-8")
    return compile_source(source, backend)


def run_source(source):
    """Compile and execute GenesisLang source."""
    python_code = compile_source(source, "python")
    # Write to temp file and execute
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(python_code)
        tmp = f.name
    try:
        result = subprocess.run([sys.executable, tmp], capture_output=True, text=True)
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        return result.returncode
    finally:
        os.unlink(tmp)


def repl():
    """Interactive REPL."""
    print("GenesisLang REPL v1.0 — GEN11")
    print('Type ".exit" to quit, ".ast" to see AST, ".py" to see Python output')
    print()
    buffer = []
    indent_level = 0

    while True:
        prompt = "... " if indent_level > 0 or buffer else ">>> "
        try:
            line = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not buffer and line.strip() == ".exit":
            break

        if not buffer and line.strip() == ".help":
            print("Commands:")
            print("  .exit  — Quit REPL")
            print("  .ast   — Show AST of last input")
            print("  .py    — Show compiled Python of last input")
            print("  .clear — Clear buffer")
            continue

        if not buffer and line.strip() == ".clear":
            buffer = []
            indent_level = 0
            continue

        buffer.append(line)

        # Count braces to handle multi-line
        opens = line.count("{")
        closes = line.count("}")
        indent_level += opens - closes

        if indent_level <= 0 and buffer:
            # Try to compile
            source = "\n".join(buffer)
            try:
                tokens = tokenize(source)
                ast = parse(tokens)
                python_code = generate_python(ast)

                if line.strip() == ".ast":
                    _print_ast(ast)
                elif line.strip() == ".py":
                    print(python_code)
                else:
                    # Execute
                    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
                        f.write(python_code)
                        tmp = f.name
                    try:
                        subprocess.run([sys.executable, tmp])
                    finally:
                        os.unlink(tmp)

            except ParseError as e:
                print(f"Parse error: {e}")
            except Exception as e:
                print(f"Error: {e}")

            buffer = []
            indent_level = 0


def _print_ast(node, indent=0):
    """Pretty-print AST."""
    prefix = "  " * indent
    if hasattr(node, "stmts"):
        print(f"{prefix}Program:")
        for s in node.stmts:
            _print_ast(s, indent + 1)
    elif node.kind in ("FnDef", "Let", "If", "For", "While", "Return", "Emit",
                       "Assign", "FnCall", "MethodCall"):
        print(f"{prefix}{node.kind}:")
        for k, v in vars(node).items():
            if k == "kind": continue
            if isinstance(v, list) and v and hasattr(v[0], "kind"):
                print(f"{prefix}  {k}:")
                for item in v:
                    _print_ast(item, indent + 2)
            elif hasattr(v, "kind"):
                print(f"{prefix}  {k}:")
                _print_ast(v, indent + 2)
            else:
                print(f"{prefix}  {k}: {v}")
    else:
        print(f"{prefix}{node.kind}: {vars(node)}")


# ═══════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("GenesisLang Compiler v1.0 — GEN11")
        print("Usage: python compiler.py [run|build|repl] [file.gen] [--js]")
        print()
        print("Commands:")
        print("  run file.gen       Compile and execute")
        print("  build file.gen     Compile to Python (print to stdout)")
        print("  build file.gen --js  Compile to JavaScript")
        print("  repl               Start interactive REPL")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "repl":
        repl()

    elif cmd == "run":
        if len(sys.argv) < 3:
            print("Usage: python compiler.py run file.gen")
            sys.exit(1)
        path = sys.argv[2]
        source = Path(path).read_text(encoding="utf-8")
        sys.exit(run_source(source))

    elif cmd == "build":
        if len(sys.argv) < 3:
            print("Usage: python compiler.py build file.gen [--js]")
            sys.exit(1)
        path = sys.argv[2]
        backend = "javascript" if "--js" in sys.argv else "python"
        result = compile_file(path, backend)
        print(result)

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
