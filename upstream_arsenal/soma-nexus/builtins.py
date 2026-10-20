"""
ΨΩ SOMA-NEXUS — Builtins Cognitivas
=====================================
Funcoes nativas do runtime. Cobrem todos os gaps do scan.psi.
"""
import os
from pathlib import Path
from .types import *


def soma_print(*args, **kwargs):
    """Emit — saida cognitiva."""
    print("[SOMA]", *args, **kwargs)


def soma_split(text: CogStr, sep: CogStr) -> CogList:
    """Split cognitivo — divide string por separador."""
    parts = str(text).split(str(sep))
    return CogList(items=[CogStr(p) for p in parts])


def soma_contains(container: CogStr, item: CogStr) -> CogBool:
    """Contains — verifica se item esta no container."""
    return CogBool(str(item) in str(container))


def soma_contains_multi(name: CogStr, *keywords: CogStr) -> CogInt:
    """Contains multi-palavra — conta quantas keywords batem no nome."""
    n = str(name).lower()
    count = sum(1 for kw in keywords if str(kw) in n)
    return CogInt(count)


def soma_to_lower(text: CogStr) -> CogStr:
    """To lowercase."""
    return CogStr(str(text).lower())


def soma_join(items: CogList, sep: CogStr) -> CogStr:
    """Join — concatena lista com separador."""
    parts = [str(i) for i in items.items]
    return CogStr(str(sep).join(parts))


def soma_list_dir(path: CogStr) -> CogList:
    """Lista diretorio."""
    p = Path(str(path))
    if p.exists() and p.is_dir():
        items = [CogStr(d.name) for d in p.iterdir() if d.is_dir()]
        return CogList(items=items)
    return CogList()


def soma_read_sample(path_pattern: CogStr, max_files: int = 10) -> CogStr:
    """Le amostra de arquivos Python (para analise de seguranca)."""
    p = Path(str(path_pattern))
    if "**" in str(path_pattern) or "*" in str(path_pattern):
        files = list(p.parent.rglob(p.name))[:max_files]
    else:
        files = [p] if p.exists() else []

    samples = []
    for f in files:
        if f.suffix == ".py":
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")[:2000]
                samples.append(content)
            except:
                pass

    return CogStr("\n---\n".join(samples))


def soma_dir_size(path: CogStr) -> CogFloat:
    """Tamanho total do diretorio em MB."""
    p = Path(str(path))
    if not p.exists():
        return CogFloat(0.0)
    total = sum(f.stat().st_size for f in p.rglob("*") if f.is_file())
    return CogFloat(total / (1024 * 1024))


def soma_extract_imports(path: CogStr) -> CogStr:
    """Extrai imports Python como assinatura."""
    import ast as pyast
    p = Path(str(path))
    imports = set()
    for f in p.rglob("*.py"):
        try:
            tree = pyast.parse(f.read_text(encoding="utf-8", errors="ignore"))
            for node in pyast.walk(tree):
                if isinstance(node, pyast.Import):
                    imports.update(a.name.split(".")[0] for a in node.names)
                elif isinstance(node, pyast.ImportFrom) and node.module:
                    imports.add(node.module.split(".")[0])
        except:
            pass
    return CogStr(",".join(sorted(imports)[:50]))


def soma_similarity(sig1: CogStr, sig2: CogStr) -> CogFloat:
    """Similaridade entre duas assinaturas (Jaccard)."""
    s1 = set(str(sig1).split(","))
    s2 = set(str(sig2).split(","))
    if not s1 or not s2:
        return CogFloat(0.0)
    intersection = len(s1 & s2)
    union = len(s1 | s2)
    return CogFloat(intersection / union * 100.0)


# Registry — mapeia nomes Ψ para funcoes Python
BUILTINS = {
    # Basicas
    "emit": soma_print,
    "int": lambda x: CogInt(int(float(str(x)))),
    "float": lambda x: CogFloat(float(str(x))),
    "count": lambda x: CogInt(len(x.items) if hasattr(x, 'items') else len(x) if hasattr(x, '__len__') else 0),
    "zeros": lambda n: CogList(items=[CogFloat(0.0)] * max(0, int(float(str(n))))),
    "range": lambda n: CogList(items=[CogInt(i) for i in range(max(0, int(float(str(n)))))]),
    "head": lambda x: x.items[0] if hasattr(x, 'items') and x.items else None,
    "last": lambda x: x.items[-1] if hasattr(x, 'items') and x.items else None,
    "clamp": lambda v, lo, hi: CogFloat(max(float(str(lo)), min(float(str(v)), float(str(hi))))),
    "contains": soma_contains,
    "join": soma_join,
    # Extendidas (SOMA-NEXUS)
    "split": soma_split,
    "contains_multi": soma_contains_multi,
    "to_lower": soma_to_lower,
    "list_dir": soma_list_dir,
    "read_sample": soma_read_sample,
    "dir_size": soma_dir_size,
    "extract_imports": soma_extract_imports,
    "similarity": soma_similarity,
    "str": lambda x: CogStr(str(x)),
}
