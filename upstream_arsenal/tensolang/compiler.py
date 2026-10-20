"""
TensoLang Compiler CLI
======================
Linguagem com Tensor Network embutida.
Compressão alienígena via SVD/MPS/TT.

Uso:
    python compiler.py run arquivo.tn
    python compiler.py repl
    python compiler.py demo
"""

import sys
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("TensoLang Compiler v1.0 — Tensor Network Language")
        print("Uso: python compiler.py [run|repl|demo] [arquivo.tn]")
        print()
        print("Comandos:")
        print("  run arquivo.tn    Compila e executa")
        print("  repl              REPL interativo")
        print("  demo              Demonstração da compressão alienígena")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "run":
        if len(sys.argv) < 3:
            print("Uso: python compiler.py run arquivo.tn")
            sys.exit(1)
        path = sys.argv[2]
        from runtime import run_file
        run_file(path)

    elif cmd == "demo":
        from tensor_core import demo
        demo()

    elif cmd == "repl":
        print("TensoLang REPL — (@ para contrair, compress() para comprimir)")
        print('Digite ".exit" para sair')
        print()
        from tokenizer import tokenize
        from parser import parse, ParseError
        from runtime import TensoRuntime
        runtime = TensoRuntime()
        buffer = []
        indent_level = 0
        while True:
            prompt = "... " if indent_level > 0 or buffer else "tns> "
            try:
                line = input(prompt)
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not buffer and line.strip() == ".exit":
                break
            buffer.append(line)
            opens = line.count("{")
            closes = line.count("}")
            indent_level += opens - closes
            if indent_level <= 0 and buffer:
                source = "\n".join(buffer)
                try:
                    tokens = tokenize(source)
                    ast = parse(tokens)
                    runtime.execute(ast)
                except ParseError as e:
                    print(f"Parse error: {e}")
                except Exception as e:
                    print(f"Error: {e}")
                buffer = []
                indent_level = 0

    else:
        print(f"Comando desconhecido: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
