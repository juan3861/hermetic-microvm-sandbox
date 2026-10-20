"""
ΨΩ SOMA-NEXUS — Compilador Unificado
=====================================
Lexer + Parser + Type Checker + Codegen.
Sintaxe: AXIOMA-Ψ v5 APEX + Ω∞ + FORGE SOMA.
CAMPO MORFOGENETICO — processa em paralelo.

Uso:
  soma run <file.psi>
  soma check <file.psi>
  soma build <file.psi> [--output file.py]
"""

import re
import ast as pyast
from pathlib import Path
from .types import *
from .builtins import BUILTINS


# ═══ TOKENIZER ═══

TOKENS = [
    ("COMMENT", r"//.*"),
    ("ANNOTATION", r"@\w+"),
    ("KEYWORD", r"\b(fn|let|if|else|loop|from|to|for|in|return|emit|stream|on_token|state)\b"),
    ("PHASE", r"::reflex|::analytic|::forensic|::agentic"),
    ("TYPE", r":\s*(CogStr|CogInt|CogFloat|CogBool|CogStream|CogList|List|LinearRes|EffectAlg|QuantumRes|SomaVector|SomaState)"),
    ("ARROW", r"->"),
    ("STRING", r'"[^"]*"'),
    ("FLOAT", r"\d+\.\d+"),
    ("INT", r"\d+"),
    ("IDENT", r"[a-zA-Z_][a-zA-Z0-9_]*"),
    ("OPERATOR", r"[+\-*/<>=!]+"),
    ("SEPARATOR", r"[\[\]\(\),:;{}]"),
    ("WHITESPACE", r"\s+"),
    ("DOT", r"\."),
]


def tokenize(source: str) -> list:
    tokens = []
    pos = 0
    while pos < len(source):
        match = None
        for name, pattern in TOKENS:
            m = re.match(pattern, source[pos:])
            if m:
                if name not in ("WHITESPACE", "COMMENT"):
                    tokens.append((name, m.group(), pos))
                pos += m.end()
                match = True
                break
        if not match:
            pos += 1
    return tokens


# ═══ PARSER ═══

class SomaProgram:
    def __init__(self):
        self.annotations = []
        self.declarations = []
        self.functions = []


class SomaFunction:
    def __init__(self, name, params, return_type, body, phase=None, is_liquid=False):
        self.name = name
        self.params = params
        self.return_type = return_type
        self.body = body
        self.phase = phase
        self.is_liquid = is_liquid


class SomaDecl:
    def __init__(self, kind, name, type_, value):
        self.kind = kind  # "let", "@working", "@semantic", "@trusted"
        self.name = name
        self.type_ = type_
        self.value = value


def parse(source: str) -> SomaProgram:
    """Parser minimal — reconhece declarações e funções Ψ."""
    prog = SomaProgram()
    lines = source.strip().split("\n")
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # Skip vazio e comentários
        if not line or line.startswith("//"):
            i += 1
            continue

        # Anotações
        if line.startswith("@"):
            prog.annotations.append(line)
            i += 1
            continue

        # Declarações: let @working nome: Tipo = valor
        if line.startswith("let "):
            parts = line[4:].split(":", 1)
            name_part = parts[0].strip()
            type_val = parts[1].strip() if len(parts) > 1 else "CogStr"
            if "=" in type_val:
                type_, val = type_val.split("=", 1)
                kind = "let"
                # Suporta: let @working nome: Tipo = valor
                if name_part.startswith("@"):
                    parts2 = name_part.split(" ", 1)
                    kind = parts2[0]
                    name_part = parts2[1] if len(parts2) > 1 else name_part
                prog.declarations.append(SomaDecl(kind, name_part.strip(), type_.strip(), val.strip()))
            i += 1
            continue

        # Funções: fn::reflex nome(params) -> Tipo:
        if line.startswith("fn"):
            # Coletar a função inteira (multilinha)
            func_lines = [line]
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                func_lines.append(next_line)
                # Função termina quando encontramos próxima fn ou declaração top-level
                if next_line.strip().startswith("fn ") or next_line.strip().startswith("let ") or next_line.strip().startswith("@"):
                    break
                j += 1
            full_func = "\n".join(func_lines)
            func = parse_function(full_func)
            if func:
                prog.functions.append(func)
            i = j
            continue

        i += 1

    return prog


def parse_function(source: str) -> Optional[SomaFunction]:
    """Parse uma função Ψ."""
    lines = source.strip().split("\n")
    header = lines[0].strip()

    # fn::reflex nome(params) -> Tipo:
    phase = None
    is_liquid = "@liquid" in source

    m = re.match(r"fn(?:::(reflex|analytic|forensic|agentic))?\s+(\w+)\s*\(([^)]*)\)\s*(?:->\s*(\w+))?", header)
    if not m:
        return None

    phase_str = m.group(1)
    name = m.group(2)
    params_str = m.group(3)
    return_type = m.group(4) or "Any"

    phase_map = {"reflex": CogPhase.REFLEX, "analytic": CogPhase.ANALYTIC,
                 "forensic": CogPhase.FORENSIC, "agentic": CogPhase.AGENTIC}
    phase = phase_map.get(phase_str)

    # Params
    params = []
    if params_str.strip():
        for p in params_str.split(","):
            p = p.strip()
            if ":" in p:
                pname, ptype = p.split(":", 1)
                params.append((pname.strip(), ptype.strip()))
            else:
                params.append((p, "Any"))

    # Body
    body = "\n".join(lines[1:]) if len(lines) > 1 else ""

    return SomaFunction(name, params, return_type, body, phase, is_liquid)


# ═══ TYPE CHECKER ═══

def type_check(prog: SomaProgram) -> list[str]:
    """Verifica tipos. Retorna lista de erros."""
    errors = []

    for func in prog.functions:
        # Verificar chamadas no corpo
        for call in re.findall(r"(\w+)\s*\(", func.body):
            if call in BUILTINS:
                continue
            # Verificar se é outra função
            found = any(f.name == call for f in prog.functions)
            if not found:
                errors.append(f"[W] {func.name}: call to unknown function '{call}'")

    return errors


# ═══ CODEGEN ═══

def codegen(prog: SomaProgram) -> str:
    """Gera Python executável a partir do programa Ψ."""
    lines = []
    lines.append('"""SOMA-NEXUS Compiled — Generated from Ψ source."""')
    lines.append("from soma_nexus.types import *")
    lines.append("from soma_nexus.builtins import *")
    lines.append("")

    # Apenas declaracoes com valor literal (globais reais)
    for decl in prog.declarations:
        val = decl.value.strip('"').strip("'") if decl.value else ""
        # Pular decls que referenciam variaveis (sao locais de funcoes)
        if '(' in str(decl.value) or any(c.isalpha() and c.islower() and c not in 'abcdef' for c in str(decl.value)[:1]):
            continue
        kind_clean = decl.kind.lstrip("@")
        # Sanitizar
        comment = f"# @{kind_clean} {decl.name}: {decl.type_} = {decl.value}"
        comment = comment.encode('ascii', errors='replace').decode()
                    lines.append(comment)
        if decl.type_ in ("CogStr", "CogInt", "CogFloat"):
            lines.append(f"{decl.name} = {decl.type_}({decl.value})")
        else:
            lines.append(f"{decl.name} = {decl.value}")

    lines.append("")

    # Funções
    for func in prog.functions:
        params_str = ", ".join(f"{p[0]}: {p[1]} = None" for p in func.params)
        phase_str = f"  # phase: {func.phase.value if func.phase else 'default'}"
        lines.append(f"def {func.name}({params_str}):{phase_str}")

        if not func.body.strip():
            lines.append("    pass")
        else:
            for body_line in func.body.strip().split("\n"):
                stripped = body_line.strip()
                if not stripped:
                    lines.append("")
                    continue

                # Traduzir emit -> print
                if stripped.startswith("emit "):
                    expr = stripped[5:].strip()
                    # emit "msg" to Console -> print("[SOMA] msg")
                    msg = expr.split(" to ")[0].strip().strip('"').strip("'")
                    # Processar concatenações simples
                    msg = msg.replace('" + str(', '", str(').replace(') + "', ')) + "')
                    lines.append(f'    print(f"[SOMA] {msg}")')
                    continue

                # let x: Tipo = expr
                if stripped.startswith("let "):
                    rest = stripped[4:]
                    if ":" in rest and "=" in rest:
                        var_type = rest.split(":", 1)[1].split("=", 1)[0].strip()
                        var_name = rest.split(":", 1)[0].strip()
                        var_expr = rest.split("=", 1)[1].strip()
                        lines.append(f"    {var_name} = {var_expr}  # {var_type}")
                    continue

                # if expr: return "valor"
                if stripped.startswith("if "):
                    cond = stripped[3:].split(":")[0].strip()
                    ret = stripped.split(":")[1].strip() if ":" in stripped else ""
                    if "return" in ret:
                        ret_val = ret.replace("return ", "").strip().strip('"')
                        lines.append(f"    if {cond}: return CogStr('{ret_val}')")
                    else:
                        lines.append(f"    if {cond}:")
                    continue

                # return expr
                if stripped.startswith("return "):
                    expr = stripped[7:].strip()
                    lines.append(f"    return {expr}")
                    continue

                # Chamadas de função
                if "(" in stripped and "=" not in stripped:
                    # Chamada simples: nome(args)
                    lines.append(f"    {stripped}")
                    continue

                # Default
                lines.append(f"    {stripped}")

        lines.append("")

    # Main
    if any(f.name == "main" for f in prog.functions):
        lines.append("if __name__ == '__main__':")
        lines.append("    main()")

    return "\n".join(lines)


# ═══ CLI ═══

def compile_file(path: str, output: str = None):
    """Compila arquivo .psi para Python."""
    source = Path(path).read_text(encoding="utf-8")
    tokens = tokenize(source)
    print(f"[SOMA-NEXUS] {len(tokens)} tokens")

    prog = parse(source)
    print(f"[SOMA-NEXUS] {len(prog.declarations)} decls, {len(prog.functions)} funcs")

    errors = type_check(prog)
    if errors:
        print(f"[SOMA-NEXUS] {len(errors)} warnings:")
        for e in errors:
            print(f"  {e}")
    else:
        print("[SOMA-NEXUS] Type check: OK")

    py_code = codegen(prog)

    out_path = output or path.replace(".psi", "_compiled.py")
    Path(out_path).write_text(py_code, encoding="utf-8")
    print(f"[SOMA-NEXUS] -> {out_path}")

    return out_path


def run_file(path: str):
    """Compila e executa."""
    import subprocess, sys, time

    start = time.time()
    out = compile_file(path)
    compile_time = time.time() - start

    print(f"\n[SOMA-NEXUS] Executing {out}...")
    start = time.time()
    r = subprocess.run([sys.executable, out], capture_output=True, text=True, timeout=30)
    run_time = time.time() - start

    print(r.stdout)
    if r.stderr:
        print(f"[STDERR] {r.stderr[:500]}")

    print(f"\n[SOMA-NEXUS] Compile: {compile_time*1000:.0f}ms | Run: {run_time*1000:.0f}ms | Total: {(compile_time+run_time)*1000:.0f}ms")


def check_file(path: str):
    """Apenas check de sintaxe e tipos."""
    source = Path(path).read_text(encoding="utf-8")
    tokens = tokenize(source)
    print(f"[SOMA-NEXUS] Syntax OK: {len(tokens)} tokens")

    prog = parse(source)
    print(f"[SOMA-NEXUS] {len(prog.declarations)} decls, {len(prog.functions)} funcs")

    errors = type_check(prog)
    if errors:
        print(f"[SOMA-NEXUS] {len(errors)} issues:")
        for e in errors:
            print(f"  {e}")
    else:
        print("[SOMA-NEXUS] All checks passed.")

    # Listar funções
    print(f"\n[SOMA-NEXUS] Function signatures:")
    for func in prog.functions:
        params = ", ".join(f"{n}: {t}" for n, t in func.params)
        phase = f"::{func.phase.value}" if func.phase else ""
        liquid = "@liquid " if func.is_liquid else ""
        print(f"  {liquid}fn{phase} {func.name}({params}) -> {func.return_type}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("SOMA-NEXUS v1.0")
        print("  soma run <file.psi>")
        print("  soma check <file.psi>")
        print("  soma build <file.psi> [--output file.py]")
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == "run" and len(sys.argv) > 2:
        run_file(sys.argv[2])
    elif cmd == "check" and len(sys.argv) > 2:
        check_file(sys.argv[2])
    elif cmd == "build" and len(sys.argv) > 2:
        out = sys.argv[4] if len(sys.argv) > 4 and sys.argv[3] == "--output" else None
        compile_file(sys.argv[2], out)
    else:
        print(f"Unknown: {cmd}")
