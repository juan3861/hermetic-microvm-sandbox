"""
TITAN-HYPERION OMEGA — Quantum-Mathematical Cortex
==================================================
Unites the 6 mathematical/quantum engines from github.com/juan3861:
  1. TensoLang (tensor_core.py): SVD Truncated Decomposition (energy=0.95) & MPS Tensor Network
  2. fastmft (Hilbert Space State Vector |psi> & Grover Diffusion Operator U_s = 2|s><s| - I)
  3. UCIP + Psi-TETO v2 (ucip.py / psiteto_v2.py): 78-95% Token & Telemetry Compression
  4. ARIA AXM v1 (axm_engine.py): 7 Mathematical Verification Lenses (Certainty = Verified / Total)
  5. GenesisLang (tokenizer.py): 4.73M tok/s Single-Pass Zero-Regex Tokenizer
  6. Phi-LLVM-JIT (phi_jit.py): Python AST -> Native x64 Machine Code via VirtualAlloc
"""

import os
import sys
import ast
import math
import time
import json
import subprocess
from typing import Dict, List, Any, Tuple, Optional

# Wire all upstream juan3861 paths
_PATHS = [
    r"F:\TITAN_HYPERION_OMEGA\upstream_arsenal\tensolang",
    r"F:\TITAN_HYPERION_OMEGA\upstream_arsenal\phi-llvm-jit\compiler",
    r"F:\TITAN_HYPERION_OMEGA\upstream_arsenal\genesislang",
    r"F:\UCIP",
    r"F:\ARIA\aria",
    r"F:\ARIA",
]
for _p in _PATHS:
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

import tensor_core as _tenso  # juan3861/tensolang
import phi_jit as _phi_jit    # juan3861/phi-llvm-jit
import tokenizer as _gen_tok  # juan3861/genesislang
import ucip as _ucip          # juan3861/UCIP
import axm_engine as _axm     # juan3861/ARIA


class QuantumMathCortex:
    """
    Executes the mathematical, tensorial, quantum-inspired, and native-x64
    transformations on target repositories inside TITAN-HYPERION OMEGA.
    """

    def __init__(self, fastmft_bin: str = r"F:\TITAN_HYPERION_OMEGA\bin\fastmft.exe"):
        self.fastmft_bin = fastmft_bin
        self.axm = _axm.AxiomaticVerificationLayer()
        self.jit = _phi_jit.PhiJIT() if os.name == "nt" else None

    # -------------------------------------------------------------------------
    # 1. TensoLang SVD & MPS Tensor Network Compression of AST Call Graphs
    # -------------------------------------------------------------------------
    def compress_ast_tensor_network(
        self,
        source_files: Dict[str, str],
        energy_threshold: float = 0.95
    ) -> Dict[str, Any]:
        """
        Builds a structural interaction matrix A (N x N) across all functions/classes
        in the repository and compresses it via TensoLang's truncated SVD and MPS.
        """
        t0 = time.perf_counter()
        symbols: List[str] = []
        calls_by_sym: Dict[str, List[str]] = {}

        for rel_path, code in sorted(source_files.items()):
            if not rel_path.endswith(".py"):
                continue
            try:
                tree = ast.parse(code)
                for node in tree.body:
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        sym_name = f"{rel_path}:{node.name}"
                        symbols.append(sym_name)
                        called = []
                        for sub in ast.walk(node):
                            if isinstance(sub, ast.Call):
                                if isinstance(sub.func, ast.Name):
                                    called.append(sub.func.id)
                                elif isinstance(sub.func, ast.Attribute):
                                    called.append(sub.func.attr)
                        calls_by_sym[sym_name] = called
            except Exception:
                continue

        n = len(symbols)
        if n == 0:
            return {
                "symbol_count": 0,
                "original_rank": 0,
                "compressed_rank": 0,
                "svd_compression_ratio": 1.0,
                "mps_compression_ratio": 1.0,
                "energy_threshold": energy_threshold,
                "elapsed_ms": round((time.perf_counter() - t0) * 1000, 3)
            }

        # Cap matrix dimension to 32x32 for fast power-iteration SVD
        dim = min(max(n, 2), 32)
        sym_subset = symbols[:dim]
        short_names = [s.split(":")[-1] for s in sym_subset]

        matrix: List[List[float]] = []
        mps = _tenso.MPS(name="repo_ast_mps")

        for i in range(dim):
            row = [0.0] * dim
            row[i] = 1.0  # Self-salience diagonal
            called_set = set(calls_by_sym.get(sym_subset[i], []))
            for j in range(dim):
                if short_names[j] in called_set:
                    row[j] += 1.5
            matrix.append(row)
            mps.add_node(row, site_name=short_names[i], energy=sum(row))

        U, S, Vt = _tenso.svd(matrix)
        U_tr, S_tr, Vt_tr = _tenso.svd_truncate(U, S, Vt, energy_threshold=energy_threshold)
        svd_ratio = _tenso.compression_ratio(U_tr, S_tr, Vt_tr, (dim, dim))
        mps_ratio = mps.compress(energy_threshold=energy_threshold)

        total_e = sum(s * s for s in S) or 1.0
        kept_e = sum(s * s for s in S_tr)

        return {
            "symbol_count": n,
            "matrix_shape": [dim, dim],
            "original_rank": len([s for s in S if s > 1e-9]),
            "compressed_rank": len(S_tr),
            "energy_retained_pct": round((kept_e / total_e) * 100.0, 2),
            "svd_compression_ratio": round(svd_ratio, 3),
            "mps_compression_ratio": round(mps_ratio, 3),
            "dominant_singular_values": [round(s, 4) for s in S_tr[:5]],
            "elapsed_ms": round((time.perf_counter() - t0) * 1000, 3)
        }

    # -------------------------------------------------------------------------
    # 2. fastmft Hardware Cartography + Hilbert Space |psi> & Grover O(sqrt(N))
    # -------------------------------------------------------------------------
    def scan_and_grover_amplify(
        self,
        root_dir: str,
        target_predicate_keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Maps directory files into a contiguous arena, computes Spatial Shannon Entropy
            H(D) = -sum p(x_i) log_2 p(x_i)
        normalizes into a Hilbert Space Quantum State Vector
            |psi> = sum_{i=0}^{N-1} alpha_i |i>
        and executes Grover's Diffusion Operator
            U_s = 2|s><s| - I
        to amplify target files in O(sqrt(N)) steps.
        Also runs compiled fastmft.exe if present on Windows.
        """
        t0 = time.perf_counter()
        keywords = [k.lower() for k in (target_predicate_keywords or ["main", "core", "engine", "compiler", "api", "auth", "security"])]

        # Collect arena of file nodes
        arena_files: List[Dict[str, Any]] = []
        ext_counts: Dict[str, int] = {}
        total_bytes = 0

        for dirpath, dirnames, filenames in os.walk(root_dir):
            dirnames[:] = [d for d in dirnames if d not in {".git", "__pycache__", "node_modules", ".pytest_cache"}]
            for fn in sorted(filenames):
                fp = os.path.join(dirpath, fn)
                try:
                    sz = os.path.getsize(fp)
                except OSError:
                    sz = 0
                rel = os.path.relpath(fp, root_dir).replace("\\", "/")
                ext = os.path.splitext(fn)[1].lower() or ".none"
                ext_counts[ext] = ext_counts.get(ext, 0) + 1
                total_bytes += sz
                arena_files.append({"index": len(arena_files), "path": rel, "size": sz, "ext": ext})

        N = len(arena_files)
        if N == 0:
            return {"file_count": 0, "shannon_entropy_bits": 0.0, "grover_iterations": 0, "amplified_targets": []}

        # 1. Spatial Shannon Entropy H(D) = -sum p(x_i) log2 p(x_i)
        shannon_h = 0.0
        for count in ext_counts.values():
            p = count / N
            if p > 0:
                shannon_h -= p * math.log2(p)

        # 2. Construct uniform superposition state |s> = (1/sqrt(N)) sum |i>
        inv_sqrt_n = 1.0 / math.sqrt(N)
        amplitudes = [inv_sqrt_n] * N

        # Identify oracle marked states M (files matching target criteria)
        marked_indices = [
            node["index"]
            for node in arena_files
            if any(kw in node["path"].lower() for kw in keywords)
        ]
        if not marked_indices:
            marked_indices = [0]

        M = len(marked_indices)
        # Optimal Grover iterations k* = floor((pi / 4) * sqrt(N / M))
        if M < N:
            grover_iters = max(1, int(math.floor((math.pi / 4.0) * math.sqrt(N / M))))
        else:
            grover_iters = 1

        marked_set = set(marked_indices)
        for _ in range(grover_iters):
            # Step A: Quantum Oracle Phase Flip U_omega |i> = -|i> for i in marked_set
            for idx in marked_set:
                amplitudes[idx] = -amplitudes[idx]

            # Step B: Grover Diffusion Operator U_s = 2|s><s| - I (Inversion about the mean)
            mean_amp = sum(amplitudes) / N
            amplitudes = [(2.0 * mean_amp) - a for a in amplitudes]

        # Compute post-amplification Born probabilities P(i) = |alpha_i|^2
        probs = [(i, amplitudes[i] * amplitudes[i]) for i in range(N)]
        probs.sort(key=lambda x: x[1], reverse=True)
        norm_check = sum(p for _, p in probs)

        top_targets = [
            {
                "path": arena_files[idx]["path"],
                "size": arena_files[idx]["size"],
                "born_probability": round(prob, 6)
            }
            for idx, prob in probs[:min(5, N)]
        ]

        # Also invoke compiled native Go fastmft.exe on Windows if available
        fastmft_native_ok = False
        if os.name == "nt" and os.path.isfile(self.fastmft_bin):
            try:
                proc = subprocess.run(
                    [self.fastmft_bin, "scan", os.path.abspath(root_dir), "--mode", "walk", "--top", "5"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                fastmft_native_ok = (proc.returncode == 0)
            except Exception:
                fastmft_native_ok = False

        return {
            "file_count": N,
            "total_bytes": total_bytes,
            "shannon_entropy_bits": round(shannon_h, 4),
            "hilbert_norm_verified": round(norm_check, 6),
            "oracle_marked_count": M,
            "classical_checks_O_N": N,
            "grover_iterations_O_sqrt_N": grover_iters,
            "amplified_top_targets": top_targets,
            "fastmft_native_go_binary_verified": fastmft_native_ok,
            "elapsed_ms": round((time.perf_counter() - t0) * 1000, 3)
        }

    # -------------------------------------------------------------------------
    # 3. UCIP + ARIA 7 Mathematical Verification Lenses + GenesisLang + Phi-JIT
    # -------------------------------------------------------------------------
    def compress_and_verify_telemetry(
        self,
        natural_instruction: str,
        action: str,
        target_path: str,
        focus: str,
        verification_report_text: str,
        known_files: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        1. Compresses Sandbox <-> Host instruction using UCIP L1/L2.
        2. Verifies the sandbox audit report through ARIA's 7 mathematical lenses.
        3. Benchmarks GenesisLang 4.73M tok/s tokenizer & Phi-LLVM-JIT native x64 execution.
        """
        # 1. UCIP Compression
        ucip_msg = _ucip.compress_l1("USR", act=action, tgt=target_path, focus=focus)
        ucip_stats = _ucip.benchmark(natural_instruction, ucip_msg)

        # 2. ARIA 7-Lens Axiomatic Verification
        axm_res = self.axm.verify(
            verification_report_text,
            context={"known_files": known_files or [target_path]}
        )

        # 3. GenesisLang Tokenizer speed check on the report text
        t_tok0 = time.perf_counter()
        tokens = _gen_tok.tokenize(verification_report_text)
        tok_elapsed = max(1e-7, time.perf_counter() - t_tok0)
        tok_per_sec = len(tokens) / tok_elapsed

        # 4. Phi-LLVM-JIT native x64 machine code execution check
        jit_proof = {"available": False}
        if self.jit is not None:
            try:
                N_gauss = 10_000_000
                res_val, ms_val = self.jit.sum_range(N_gauss)
                expected_val = N_gauss * (N_gauss + 1) // 2
                jit_proof = {
                    "available": True,
                    "operation": f"sum_1_to_n({N_gauss})",
                    "x64_result": res_val,
                    "expected": expected_val,
                    "verified": (res_val == expected_val),
                    "exec_ms": round(ms_val, 5)
                }
            except Exception as e:
                jit_proof = {"available": False, "error": str(e)}

        return {
            "ucip_compressed_wire": ucip_msg,
            "ucip_token_savings_pct": ucip_stats["savings_percent"],
            "ucip_compression_ratio": ucip_stats.get("compression_ratio", 1.0),
            "aria_7_lenses": {
                "score": axm_res["score"],
                "certainty": axm_res["certainty"],
                "verdict": axm_res["verdict"],
                "passed_lenses": axm_res["passed_lenses"],
                "failed_lenses": axm_res["failed_lenses"],
                "verified_claims": axm_res["verified_claims"],
                "total_claims": axm_res["total_claims"]
            },
            "genesislang_tokenizer": {
                "token_count": len(tokens),
                "throughput_tok_per_sec": round(tok_per_sec, 1)
            },
            "phi_llvm_jit_x64": jit_proof
        }
