"""
TITAN-HYPERION OMEGA — Quantum-Topological Cartographer (Córtex AGI)
===================================================================
Fuses:
  - AST Multi-scale Semantic DAG (ast + networkx)
  - TensoLang Adjacency Matrix SVD Decomposition (Eigenspace of Logic)
  - fastmft Information-Theoretic Shannon Entropy H(D)
  - Hilbert Space State Vector |psi> & Grover Diffusion Operator O(sqrt(N))
"""

import os
import ast
import math
import time
import numpy as np
import networkx as nx
from typing import Dict, List, Any, Optional, Tuple, Set


class ASTVisitorGraphBuilder(ast.NodeVisitor):
    """
    Traverses Python AST to construct an intra-module symbol dependency graph.
    """
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.graph = nx.DiGraph()
        self.current_scope: Optional[str] = None
        self.symbol_source_lines: Dict[str, Tuple[int, int]] = {}
        self.symbol_tokens: Dict[str, List[str]] = {}

    def _qual(self, name: str) -> str:
        if self.current_scope:
            return f"{self.module_name}.{self.current_scope}.{name}"
        return f"{self.module_name}.{name}"

    def visit_ClassDef(self, node: ast.ClassDef):
        class_name = self._qual(node.name)
        self.graph.add_node(class_name, type="class", lineno=node.lineno, name=node.name, module=self.module_name)
        self.symbol_source_lines[class_name] = (node.lineno, getattr(node, "end_lineno", node.lineno))
        
        # Base inheritance edges
        for base in node.bases:
            if isinstance(base, ast.Name):
                self.graph.add_edge(class_name, f"{self.module_name}.{base.id}", relation="inherits")

        old_scope = self.current_scope
        self.current_scope = node.name
        self.generic_visit(node)
        self.current_scope = old_scope

    def visit_FunctionDef(self, node: ast.FunctionDef):
        func_name = self._qual(node.name)
        self.graph.add_node(func_name, type="function", lineno=node.lineno, name=node.name, module=self.module_name)
        self.symbol_source_lines[func_name] = (node.lineno, getattr(node, "end_lineno", node.lineno))
        
        # Gather token-level names for entropy analysis
        tokens = [n.id for n in ast.walk(node) if isinstance(n, ast.Name)]
        self.symbol_tokens[func_name] = tokens

        # Connect caller to current scope if inside class
        if self.current_scope:
            parent = f"{self.module_name}.{self.current_scope}"
            self.graph.add_edge(parent, func_name, relation="contains")

        # Find function calls
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    target = f"{self.module_name}.{child.func.id}"
                    self.graph.add_edge(func_name, target, relation="calls")
                elif isinstance(child.func, ast.Attribute) and isinstance(child.func.value, ast.Name):
                    target = f"{self.module_name}.{child.func.attr}"
                    self.graph.add_edge(func_name, target, relation="calls_attr")

        old_scope = self.current_scope
        self.current_scope = node.name
        self.generic_visit(node)
        self.current_scope = old_scope

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        # Treat async functions similarly
        func_name = self._qual(node.name)
        self.graph.add_node(func_name, type="async_function", lineno=node.lineno, name=node.name, module=self.module_name)
        self.symbol_source_lines[func_name] = (node.lineno, getattr(node, "end_lineno", node.lineno))
        tokens = [n.id for n in ast.walk(node) if isinstance(n, ast.Name)]
        self.symbol_tokens[func_name] = tokens
        self.generic_visit(node)


class QuantumTopologicalCartographer:
    """
    AGI-grade Code Cartographer:
    Constructs the global topological manifold, applies SVD spectral decomposition,
    computes Shannon entropy, constructs the Hilbert state |psi>, and applies Grover search.
    """

    def __init__(self):
        self.global_graph = nx.DiGraph()
        self.symbol_tokens: Dict[str, List[str]] = {}
        self.symbol_entropy: Dict[str, float] = {}

    def ingest_codebase(self, files_dict: Dict[str, str]) -> nx.DiGraph:
        """
        Parses all Python source files and merges them into the global dependency graph.
        """
        self.global_graph.clear()
        self.symbol_tokens.clear()
        self.symbol_entropy.clear()

        for rel_path, code in files_dict.items():
            if not rel_path.endswith(".py"):
                continue
            mod_name = os.path.splitext(rel_path.replace("\\", "/"))[0].replace("/", ".")
            try:
                tree = ast.parse(code, filename=rel_path)
            except SyntaxError:
                continue

            visitor = ASTVisitorGraphBuilder(mod_name)
            visitor.visit(tree)

            self.global_graph = nx.compose(self.global_graph, visitor.graph)
            self.symbol_tokens.update(visitor.symbol_tokens)

        # Compute Shannon entropy for each symbol
        for sym, tokens in self.symbol_tokens.items():
            self.symbol_entropy[sym] = self._compute_token_shannon_entropy(tokens)

        return self.global_graph

    def _compute_token_shannon_entropy(self, tokens: List[str]) -> float:
        if not tokens:
            return 0.0
        counts: Dict[str, int] = {}
        for t in tokens:
            counts[t] = counts.get(t, 0) + 1
        n = float(len(tokens))
        h = 0.0
        for c in counts.values():
            p = c / n
            if p > 0:
                h -= p * math.log2(p)
        return round(h, 4)

    def compute_eigenspace_svd(self, energy_threshold: float = 0.95) -> Dict[str, Any]:
        """
        Computes the Singular Value Decomposition of the codebase adjacency matrix.
        Extracts the logical spine (Principal Eigenvector u_1).
        """
        nodes = sorted(list(self.global_graph.nodes()))
        n = len(nodes)
        if n == 0:
            return {"error": "Empty codebase graph", "n_nodes": 0}

        node_to_idx = {name: i for i, name in enumerate(nodes)}
        adj = np.zeros((n, n), dtype=np.float64)

        for u, v in self.global_graph.edges():
            if u in node_to_idx and v in node_to_idx:
                adj[node_to_idx[u], node_to_idx[v]] = 1.0

        # Perform SVD: A = U * S * Vh
        try:
            U, S, Vh = np.linalg.svd(adj, full_matrices=False)
        except np.linalg.LinAlgError:
            S = np.ones(n, dtype=np.float64)
            U = np.eye(n, dtype=np.float64)

        total_variance = np.sum(S ** 2) if np.sum(S ** 2) > 0 else 1.0
        explained_variance_ratio = (S ** 2) / total_variance
        cumulative_energy = np.cumsum(explained_variance_ratio)

        # Determine rank k for target energy threshold
        k = int(np.searchsorted(cumulative_energy, energy_threshold)) + 1
        k = min(k, n)

        # Principal Eigenvector: First column of U (left singular vector u_1)
        u_1 = np.abs(U[:, 0]) if U.shape[1] > 0 else np.ones(n) / math.sqrt(n)
        u1_norm = np.linalg.norm(u_1)
        if u1_norm > 0:
            u_1 = u_1 / u1_norm

        topological_centrality = {nodes[i]: round(float(u_1[i]), 5) for i in range(n)}
        ranked_nodes = sorted(topological_centrality.items(), key=lambda x: x[1], reverse=True)

        return {
            "total_nodes": n,
            "total_edges": self.global_graph.number_of_edges(),
            "singular_values": [round(float(s), 4) for s in S[:10]],
            "retained_rank_k": k,
            "retained_energy": round(float(cumulative_energy[k - 1]) if k <= len(cumulative_energy) else 1.0, 4),
            "topological_spine_top5": ranked_nodes[:5],
            "node_centrality": topological_centrality
        }

    def construct_hilbert_state(self) -> Tuple[np.ndarray, List[str]]:
        """
        Constructs the normalized Hilbert state vector |psi> = sum alpha_i |symbol_i>.
        alpha_i incorporates both topological centrality (u_1) and Shannon entropy H(D).
        """
        nodes = sorted(list(self.global_graph.nodes()))
        n = len(nodes)
        if n == 0:
            return np.array([1.0]), ["empty"]

        svd_res = self.compute_eigenspace_svd()
        centrality = svd_res.get("node_centrality", {})

        raw_weights = []
        for name in nodes:
            cent = centrality.get(name, 0.01)
            ent = self.symbol_entropy.get(name, 0.1)
            # Organ weight = Centrality * (1 + Entropy)
            w = (cent + 0.001) * (1.0 + ent)
            raw_weights.append(w)

        raw_arr = np.array(raw_weights, dtype=np.float64)
        norm = np.linalg.norm(raw_arr)
        if norm > 0:
            alpha = raw_arr / norm
        else:
            alpha = np.ones(n, dtype=np.float64) / math.sqrt(n)

        return alpha, nodes

    def grover_quantum_search(
        self,
        target_keywords: List[str],
        max_iterations: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Executes Grover's quantum diffusion algorithm to amplify the amplitude
        of target capability capsules in O(sqrt(N)) steps.
        """
        t0 = time.perf_counter()
        alpha, nodes = self.construct_hilbert_state()
        n = len(nodes)
        if n == 0:
            return {"error": "Empty state space"}

        # Identify target oracle states (predicate match)
        target_indices: Set[int] = set()
        lowered_kw = [k.lower() for k in target_keywords]
        for i, name in enumerate(nodes):
            name_lower = name.lower()
            tokens_lower = [t.lower() for t in self.symbol_tokens.get(name, [])]
            if any(k in name_lower for k in lowered_kw) or any(k in tokens_lower for k in lowered_kw):
                target_indices.add(i)

        m = len(target_indices)
        if m == 0:
            # Fallback: oracle matches highest entropy node
            fallback_idx = int(np.argmax(alpha))
            target_indices.add(fallback_idx)
            m = 1

        # Optimal Grover iterations: R approx round(pi/4 * sqrt(N/M))
        optimal_r = max(1, int(round((math.pi / 4.0) * math.sqrt(float(n) / float(m)))))
        num_iter = min(optimal_r, max_iterations or 15)

        # Uniform superposition state |s>
        s_vec = np.ones(n, dtype=np.float64) / math.sqrt(n)
        current_state = np.copy(alpha)

        for _ in range(num_iter):
            # Phase Inversion (Oracle U_omega)
            for idx in target_indices:
                current_state[idx] = -current_state[idx]

            # Inversion about the mean (Diffusion Operator U_s = 2|s><s| - I)
            mean_amp = np.mean(current_state)
            current_state = 2.0 * mean_amp - current_state

        # Normalize state
        state_norm = np.linalg.norm(current_state)
        if state_norm > 0:
            current_state = current_state / state_norm

        probabilities = np.square(np.abs(current_state))
        top_indices = np.argsort(probabilities)[::-1]

        amplified_targets = []
        for rank, idx in enumerate(top_indices[:5]):
            sym_name = nodes[idx]
            amplified_targets.append({
                "rank": rank + 1,
                "symbol": sym_name,
                "probability": round(float(probabilities[idx]), 5),
                "is_oracle_hit": (idx in target_indices),
                "entropy_bits": self.symbol_entropy.get(sym_name, 0.0),
                "node_type": self.global_graph.nodes[sym_name].get("type", "unknown")
            })

        return {
            "state_space_dim_N": n,
            "oracle_targets_M": m,
            "grover_iterations_run": num_iter,
            "theoretical_complexity": f"O(sqrt({n}/{m})) = ~{optimal_r} ops",
            "top_amplified_organs": amplified_targets,
            "best_target_symbol": amplified_targets[0]["symbol"] if amplified_targets else None,
            "elapsed_ms": round((time.perf_counter() - t0) * 1000, 3)
        }

    def extract_dependency_closure(self, target_symbol: str) -> List[str]:
        """
        Extracts the full backward dependency closure (all symbols required to execute target_symbol).
        """
        if target_symbol not in self.global_graph:
            return [target_symbol]
        
        # Descendants in directed graph (callees, bases, dependencies)
        closure = nx.descendants(self.global_graph, target_symbol)
        closure.add(target_symbol)
        return sorted(list(closure))
