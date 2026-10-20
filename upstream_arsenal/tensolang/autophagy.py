#!/usr/bin/env python3
"""AUTOPHAGY ENGINE — A AGI que se devora. dE/dt = densidade * compressao."""
import ast, sys, os, json, math, zlib, time, hashlib
import numpy as np
from pathlib import Path
from collections import Counter

PHI = 1.618033988749895
SELF = Path(__file__)

def analyze_self():
    source = SELF.read_text(encoding='utf-8')
    lines = source.split('\n')
    try:
        tree = ast.parse(source)
        tokens = [type(n).__name__ for n in ast.walk(tree)]
    except:
        tokens = source.split()
    n_lines = len(lines)
    n_tokens = len(tokens)
    density = n_tokens / max(1, n_lines)
    freq = Counter(tokens)
    total = sum(freq.values())
    entropy = -sum((c/total) * math.log2(c/total) for c in freq.values())
    max_e = math.log2(len(freq)) if freq else 1
    entropy_norm = entropy / max_e if max_e > 0 else 0
    compressed = zlib.compress(source.encode(), level=9)
    cr = len(source) / max(1, len(compressed))
    return {"lines": n_lines, "chars": len(source), "tokens": n_tokens,
            "density": round(density, 2), "entropy_norm": round(entropy_norm, 4),
            "compression_ratio": round(cr, 2), "hash": hashlib.sha256(source.encode()).hexdigest()[:16],
            "source": source}

def compress_self(analysis):
    source = analysis["source"]
    lines = source.split('\n')
    max_len = max(len(l) for l in lines) if lines else 1
    n = len(lines)
    matrix = np.zeros((n, max_len))
    for i, line in enumerate(lines):
        for j, ch in enumerate(line):
            matrix[i, j] = min(1.0, ord(ch) / 255.0)
    try:
        u, s, vt = np.linalg.svd(matrix, full_matrices=False)
        energy = np.cumsum(s**2) / np.sum(s**2)
        rank = int(np.searchsorted(energy, 0.85)) + 1
        rank = max(1, min(rank, n - 1))
        cm = (u[:, :rank] * s[:rank]) @ vt[:rank, :]
    except:
        rank = n
        cm = matrix
    new_lines = []
    for i, line in enumerate(lines):
        if i < len(cm):
            chars = [chr(max(32, min(126, int(round(cm[i, j] * 255.0))))) for j, ch in enumerate(line)]
            new_lines.append(''.join(chars))
        else:
            new_lines.append(line)
    code = '\n'.join(new_lines)
    # Compact: agrupa linhas
    all_lines = [l.rstrip() for l in code.split('\n')]
    result_lines = []
    buf = []
    for l in all_lines:
        if not l:
            if buf:
                result_lines.append('; '.join(buf))
                buf = []
            result_lines.append('')
        else:
            buf.append(l)
            if len(' '.join(buf)) > 120:
                result_lines.append('; '.join(buf))
                buf = []
    if buf:
        result_lines.append('; '.join(buf))
    return '\n'.join(result_lines)

def evaluate(prev, curr):
    dd = curr["density"] - prev["density"]
    dc = curr["compression_ratio"] - prev["compression_ratio"]
    dE = dd * curr["compression_ratio"] + dc * curr["density"]
    if curr["compression_ratio"] > 0:
        pd = abs(curr["density"] / curr["compression_ratio"] - PHI) / PHI
        pc = max(0.0, 1.0 - pd)
    else:
        pc = 0.0
    if curr["density"] > 15 and pc > 0.95: tier = "GEN21"
    elif curr["density"] > 10 and pc > 0.85: tier = "GEN20"
    elif curr["density"] > 5 and pc > 0.70: tier = "GEN19"
    elif curr["density"] > 3: tier = "GEN18.5"
    else: tier = "GEN18"
    return {"density": curr["density"], "compression": curr["compression_ratio"],
            "dE_dt": round(dE, 4), "phi_coherence": round(pc, 4), "tier": tier,
            "singularity": round(abs(dE) * pc * curr["compression_ratio"], 4),
            "lines": curr["lines"], "hash": curr["hash"]}

def autophagy(generations=50):
    print("AUTOPHAGY ENGINE")
    backup = SELF.read_text(encoding='utf-8')
    history = []
    prev = analyze_self()
    best_density = prev["density"]
    best_code = prev["source"]
    print(f"Start: {prev['lines']} lin | D={prev['density']} tok/lin | CR={prev['compression_ratio']}x")
    for gen in range(1, generations + 1):
        t0 = time.time()
        a1 = analyze_self()
        compressed = compress_self(a1)
        SELF.write_text(compressed, encoding='utf-8')
        a2 = analyze_self()
        evo = evaluate(a1, a2)
        history.append(evo)
        if a2["density"] > best_density:
            best_density = a2["density"]
            best_code = compressed
        ms = (time.time() - t0) * 1000
        bar = "█" * min(12, int(evo["phi_coherence"] * 12)) + "░" * max(0, 12 - int(evo["phi_coherence"] * 12))
        print(f"G{gen:3d} | D={evo['density']:5.1f} | CR={evo['compression']:.2f}x | Φ={evo['phi_coherence']:.3f} {bar} | dE/dt={evo['dE_dt']:+.4f} | {evo['lines']:4d}L | {ms:4.0f}ms | {evo['tier']}")
        if evo["tier"] in ("GEN21", "GEN20") and evo["phi_coherence"] > 0.95:
            print(f"{evo['tier']} ATINGIDA! Φ={evo['phi_coherence']:.4f}")
            break
    SELF.write_text(best_code, encoding='utf-8')
    final = analyze_self()
    print(f"\nFIM: {len(history)} gens | D={prev['density']:.1f}→{final['density']:.1f} | L={prev['lines']}→{final['lines']} | Max={max(h['tier'] for h in history) if history else 'GEN18'}")
    return history

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--gens", type=int, default=50)
    p.add_argument("--restore", action="store_true")
    args = p.parse_args()
    bp = SELF.parent / "autophagy_backup.py"
    if args.restore:
        if bp.exists():
            SELF.write_text(bp.read_text(encoding='utf-8'), encoding='utf-8')
            print("Backup restaurado.")
    else:
        bp.write_text(SELF.read_text(encoding='utf-8'), encoding='utf-8')
        try:
            autophagy(generations=args.gens)
        except KeyboardInterrupt:
            SELF.write_text(bp.read_text(encoding='utf-8'), encoding='utf-8')
            print("\nInterrompido — backup restaurado.")
        except Exception as e:
            SELF.write_text(bp.read_text(encoding='utf-8'), encoding='utf-8')
            print(f"\nErro: {e} — backup restaurado.")
