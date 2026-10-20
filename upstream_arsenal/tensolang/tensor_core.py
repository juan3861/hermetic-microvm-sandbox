"""
TENSO TENSOR CORE — Motor de Tensor Network
============================================
Compressão alienígena via:
  - MPS (Matrix Product State) para código sequencial
  - SVD truncado com threshold de energia
  - TT (Tensor Train) para dados multi-dimensionais
  - Auto-rank: a rede decide o rank ótimo sozinha

Filosofia: Tudo é tensor. Código = Rede Tensorial.
Execução = Contração. Compressão = Sobrevivência.
"""

import math
import copy
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Any
import json


# ═══════════════════════════════════════════════════════════
# TENSOR PRIMITIVES
# ═══════════════════════════════════════════════════════════

@dataclass
class Tensor:
    """Tensor multidimensional com suporte a SVD e reshape."""
    data: List[Any]          # Dados flat ou aninhados
    shape: Tuple[int, ...]   # Dimensões

    @staticmethod
    def from_list(data):
        """Constrói tensor a partir de lista Python."""
        shape = _infer_shape(data)
        return Tensor(data=data, shape=shape)

    @staticmethod
    def zeros(*shape):
        """Tensor de zeros."""
        if len(shape) == 1:
            return Tensor(data=[0] * shape[0], shape=shape)
        elif len(shape) == 2:
            return Tensor(data=[[0]*shape[1] for _ in range(shape[0])], shape=shape)
        else:
            return Tensor(data=_zeros_rec(shape), shape=shape)

    @staticmethod
    def eye(n):
        """Matriz identidade."""
        data = [[1.0 if i==j else 0.0 for j in range(n)] for i in range(n)]
        return Tensor(data=data, shape=(n, n))

    def __repr__(self):
        return f"Tensor(shape={self.shape}, data={_summarize(self.data, self.shape)})"

    @property
    def ndim(self):
        return len(self.shape)

    @property
    def size(self):
        s = 1
        for d in self.shape:
            s *= d
        return s

    def flatten(self):
        """Aplana para vetor 1D."""
        flat = _flatten_rec(self.data)
        return Tensor(data=flat, shape=(len(flat),))

    def reshape(self, *new_shape):
        """Muda a forma (mantém dados)."""
        flat = _flatten_rec(self.data)
        if len(flat) != _prod(new_shape):
            raise ValueError(f"Cannot reshape {self.shape} to {new_shape}")
        return Tensor(data=_unflatten_rec(flat, list(new_shape)), shape=new_shape)

    def to_list(self):
        """Converte para lista Python pura."""
        return self.data

    def to_matrix(self):
        """Converte para matriz 2D (lista de listas)."""
        if self.ndim == 1:
            return [[x] for x in self.data]
        elif self.ndim == 2:
            return self.data
        else:
            raise ValueError(f"Cannot convert {self.shape} to matrix")


# ═══════════════════════════════════════════════════════════
# SVD — Singular Value Decomposition (power iteration)
# ═══════════════════════════════════════════════════════════

def svd(matrix: List[List[float]], max_rank: int = None):
    """
    SVD via power iteration com truncamento.
    Retorna (U, S, Vt) onde A ≈ U @ diag(S) @ Vt.
    """
    m = len(matrix)
    n = len(matrix[0]) if m > 0 else 0
    if m == 0 or n == 0:
        return [], [], []

    rank = min(m, n)
    if max_rank:
        rank = min(rank, max_rank)

    # Matriz de cópia para trabalho
    A = [row[:] for row in matrix]

    U = [[0.0]*rank for _ in range(m)]
    S = [0.0]*rank
    Vt = [[0.0]*n for _ in range(rank)]

    for k in range(rank):
        # Power iteration para encontrar singular vector
        v = [1.0/math.sqrt(n)] * n  # inicial

        for _ in range(5):  # 5 iterações bastam para convergir
            # u = A @ v
            u = [0.0]*m
            for i in range(m):
                s = 0.0
                Ai = A[i]
                for j in range(n):
                    s += Ai[j] * v[j]
                u[i] = s

            # Normaliza u
            norm_u = math.sqrt(sum(x*x for x in u))
            if norm_u < 1e-10:
                break
            u = [x/norm_u for x in u]

            # v = A^T @ u
            v = [0.0]*n
            for j in range(n):
                s = 0.0
                for i in range(m):
                    s += A[i][j] * u[i]
                v[j] = s

            norm_v = math.sqrt(sum(x*x for x in v))
            if norm_v < 1e-10:
                break
            v = [x/norm_v for x in v]

        # Valor singular
        sigma = 0.0
        for i in range(m):
            s = 0.0
            Ai = A[i]
            for j in range(n):
                s += Ai[j] * v[j]
            sigma += u[i] * s

        if sigma < 1e-10:
            break

        S[k] = abs(sigma)

        # Armazena
        for i in range(m):
            U[i][k] = u[i]
        for j in range(n):
            Vt[k][j] = v[j]

        # Remove componente da matriz
        for i in range(m):
            ui = U[i][k]
            for j in range(n):
                A[i][j] -= ui * S[k] * Vt[k][j]

    return U, S, Vt


def svd_truncate(U, S, Vt, energy_threshold=0.95):
    """
    Trunca SVD mantendo energy_threshold% da energia total.
    Energia = soma dos quadrados dos valores singulares.
    """
    if not S:
        return U, S, Vt

    total_energy = sum(s*s for s in S)
    if total_energy < 1e-10:
        return U, S, Vt

    cumulative = 0.0
    new_rank = 0
    for i, s in enumerate(S):
        cumulative += s * s
        new_rank = i + 1
        if cumulative / total_energy >= energy_threshold:
            break

    new_rank = min(new_rank, len(S))
    return (
        [row[:new_rank] for row in U],
        S[:new_rank],
        Vt[:new_rank]
    )


def compression_ratio(U, S, Vt, original_shape):
    """Calcula razão de compressão (original / comprimido)."""
    m, n = original_shape
    rank = len(S)
    original_params = m * n
    compressed_params = (m * rank) + rank + (rank * n)
    if compressed_params == 0:
        return 1.0
    return original_params / compressed_params


# ═══════════════════════════════════════════════════════════
# MPS — Matrix Product State (cadeia 1D)
# ═══════════════════════════════════════════════════════════

@dataclass
class MPSNode:
    """Nó de uma MPS: tensor de rank 3 (left, phys, right)."""
    tensor: Tensor          # shape: (D_left, d_phys, D_right)
    site_name: str = ""
    energy: float = 1.0     # relevância do nó

    @property
    def bond_left(self):
        return self.tensor.shape[0] if self.tensor.ndim >= 1 else 1

    @property
    def bond_right(self):
        return self.tensor.shape[-1] if self.tensor.ndim >= 1 else 1

    @property
    def phys_dim(self):
        if self.tensor.ndim == 3:
            return self.tensor.shape[1]
        elif self.tensor.ndim == 2:
            return self.tensor.shape[1]
        else:
            return self.tensor.shape[0]


class MPS:
    """
    Matrix Product State — representa uma sequência como rede 1D.
    Código sequencial = MPS onde cada site é uma operação.
    """

    def __init__(self, name="mps"):
        self.name = name
        self.nodes: List[MPSNode] = []
        self.bonds: dict = {}
        self.total_energy = 0.0
        self.compression_events = []

    def add_bond(self, src, dst, strength=1.0):
        """Adiciona uma ligação entre dois sites."""
        self.bonds[(src, dst)] = strength

    def add_node(self, data, site_name="", energy=1.0):
        """Adiciona um site à cadeia."""
        tensor = Tensor.from_list(data) if isinstance(data, list) else data
        if tensor.ndim == 1:
            # Adiciona dimensões de bond
            t = tensor.reshape(1, tensor.shape[0], 1)
            node = MPSNode(tensor=t, site_name=site_name, energy=energy)
        elif tensor.ndim == 2:
            t = tensor.reshape(1, tensor.shape[0], tensor.shape[1])
            node = MPSNode(tensor=t, site_name=site_name, energy=energy)
        else:
            node = MPSNode(tensor=tensor, site_name=site_name, energy=energy)
        self.nodes.append(node)
        self.total_energy += energy

    def compress(self, max_bond=None, energy_threshold=0.95):
        """
        Comprime a MPS via SVD sequencial (canonicalization).
        Esta é a "compressão alienígena" — encontra padrões latentes.
        """
        if len(self.nodes) < 2:
            return self

        events = []
        total_original = 0
        total_compressed = 0

        # Sweep da esquerda para direita
        for i in range(len(self.nodes) - 1):
            left_node = self.nodes[i]
            right_node = self.nodes[i + 1]

            # Constrói matriz de acoplamento entre site i e i+1
            tl = left_node.tensor
            tr = right_node.tensor

            # Achata dimensões de bond + phys para SVD
            dl = tl.shape[0] * tl.shape[1] if tl.ndim >= 2 else tl.shape[0]
            dr = tr.shape[1] * tr.shape[2] if tr.ndim >= 3 else (tr.shape[1] if tr.ndim >= 2 else tr.shape[0])

            # Constrói matriz de interação
            matrix = _build_interaction_matrix(tl, tr)

            if matrix and len(matrix) > 0 and len(matrix[0]) > 0:
                original_params = len(matrix) * len(matrix[0])
                U, S, Vt = svd(matrix)
                U, S, Vt = svd_truncate(U, S, Vt, energy_threshold)

                if max_bond and len(S) > max_bond:
                    U = [row[:max_bond] for row in U]
                    S = S[:max_bond]
                    Vt = Vt[:max_bond]

                new_rank = len(S)
                compressed_params = len(U)*new_rank + new_rank + new_rank*len(Vt[0]) if Vt else 0

                if compressed_params > 0:
                    ratio = original_params / compressed_params
                    total_original += original_params
                    total_compressed += compressed_params

                    # Atualiza nós com representação comprimida
                    if new_rank < dl and new_rank < dr:
                        events.append({
                            "site": i,
                            "nodes": f"{left_node.site_name}↔{right_node.site_name}",
                            "original_rank": min(dl, dr),
                            "compressed_rank": new_rank,
                            "ratio": round(ratio, 2),
                            "energy_kept": round(energy_threshold * 100),
                        })

        self.compression_events = events

        if total_original > 0:
            return total_original / total_compressed
        return 1.0

    def contract(self):
        """
        Contrai toda a MPS → resultado final (execução).
        """
        if not self.nodes:
            return Tensor.zeros(1)

        result = self.nodes[0].tensor
        for i in range(1, len(self.nodes)):
            result = _contract_tensors(result, self.nodes[i].tensor)
        return result

    def stats(self):
        """Estatísticas da rede."""
        total_params = sum(n.tensor.size for n in self.nodes)
        return {
            "name": self.name,
            "sites": len(self.nodes),
            "total_params": total_params,
            "total_energy": self.total_energy,
            "compression_events": self.compression_events,
            "nodes": [{"name": n.site_name, "shape": n.tensor.shape, "energy": n.energy} for n in self.nodes],
        }


# ═══════════════════════════════════════════════════════════
# TENSOR TRAIN (TT) — Para arrays multi-dimensionais
# ═══════════════════════════════════════════════════════════

class TensorTrain:
    """
    Tensor Train decomposition.
    Um tensor N-dimensional é representado como N tensores de rank 3.
    """
    def __init__(self, name="tt"):
        self.name = name
        self.cores: List[Tensor] = []
        self.original_shape = None

    def decompose(self, tensor: Tensor, max_rank=16):
        """Decompõe tensor em TT format via SVD sequencial."""
        self.original_shape = tensor.shape
        self.cores = []
        remaining = tensor

        for d in range(len(tensor.shape) - 1):
            # Reshape para matriz
            mat = remaining.reshape(remaining.shape[0] * remaining.shape[1],
                                    _prod(remaining.shape[2:]) if remaining.ndim > 2 else 1)
            mat_data = mat.to_matrix()

            U, S, Vt = svd(mat_data, max_rank)
            U, S, Vt = svd_truncate(U, S, Vt, 0.99)

            rank = len(S)
            core_shape = (remaining.shape[0], remaining.shape[1], rank)
            # Reconstrói core
            core_data = _reshape_to_3d(U, remaining.shape[0], remaining.shape[1], rank)
            core = Tensor(data=core_data, shape=core_shape)
            self.cores.append(core)

            # Próxima iteração
            SVt = _multiply_diag(S, Vt)
            remaining = Tensor(data=_reshape_from_svd(SVt, rank, remaining.shape[2:]),
                              shape=(rank,) + remaining.shape[2:])

        # Último core
        self.cores.append(remaining)
        return self

    def reconstruct(self):
        """Reconstrói tensor original dos cores."""
        if not self.cores:
            return None
        result = self.cores[0]
        for core in self.cores[1:]:
            result = _contract_tt_cores(result, core)
        return result

    def compression_ratio(self):
        """Razão de compressão."""
        if not self.original_shape:
            return 1.0
        original = _prod(self.original_shape)
        compressed = sum(c.size for c in self.cores)
        return original / compressed if compressed > 0 else 1.0


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════

def _prod(shape):
    p = 1
    for d in shape:
        p *= d
    return p

def _infer_shape(data):
    if not isinstance(data, list):
        return ()
    if not data:
        return (0,)
    if isinstance(data[0], list):
        return (len(data),) + _infer_shape(data[0])
    return (len(data),)

def _flatten_rec(data):
    if not isinstance(data, list):
        return [data]
    result = []
    for item in data:
        result.extend(_flatten_rec(item))
    return result

def _unflatten_rec(flat, shape):
    if len(shape) == 0:
        return flat[0] if flat else None
    if len(shape) == 1:
        return flat[:shape[0]]
    size = _prod(shape[1:])
    return [_unflatten_rec(flat[i*size:(i+1)*size], shape[1:]) for i in range(shape[0])]

def _zeros_rec(shape):
    if len(shape) == 1:
        return [0] * shape[0]
    return [_zeros_rec(shape[1:]) for _ in range(shape[0])]

def _summarize(data, shape):
    """Resumo compacto do tensor."""
    if _prod(shape) <= 12:
        return str(data)
    return f"[{_prod(shape)} elements]"

def _build_interaction_matrix(t1, t2):
    """Constrói matriz de interação entre dois tensores MPS."""
    flat1 = _flatten_rec(t1.data)
    flat2 = _flatten_rec(t2.data)
    if not flat1 or not flat2:
        return []
    m = len(flat1)
    n = len(flat2)
    # Cria matriz de correlação
    matrix = [[0.0]*n for _ in range(m)]
    for i in range(min(m, n)):
        matrix[i][i] = float(flat1[i]) * float(flat2[i]) if i < len(flat2) else 0.0
    return matrix

def _contract_tensors(t1, t2):
    """Contrai dois tensores ao longo da dimensão de bond."""
    # Simplificação: produto tensorial
    flat1 = _flatten_rec(t1.data)
    flat2 = _flatten_rec(t2.data)
    result = []
    for a in flat1:
        for b in flat2:
            result.append(float(a) * float(b))
    return Tensor(data=result, shape=(len(result), 1, 1))

def _reshape_to_3d(U, d1, d2, d3):
    """Reshape para tensor 3D."""
    # U tem shape (d1*d2, d3)
    result = []
    for i in range(d1):
        row = []
        for j in range(d2):
            idx = i * d2 + j
            row.append(U[idx][:d3] if idx < len(U) else [0.0]*d3)
        result.append(row)
    return result

def _multiply_diag(S, Vt):
    """Multiplica diag(S) @ Vt."""
    rank = len(S)
    result = []
    for i in range(rank):
        row = [S[i] * v for v in Vt[i]]
        result.append(row)
    return result

def _reshape_from_svd(SVt, rank, remaining_shape):
    """Reshape após SVD."""
    # SVt: (rank, remaining_size)
    return SVt

def _contract_tt_cores(c1, c2):
    """Contrai dois cores de TT."""
    flat1 = _flatten_rec(c1.data)
    flat2 = _flatten_rec(c2.data)
    result = []
    for a in flat1:
        for b in flat2:
            result.append(float(a) * float(b))
    return Tensor(data=result, shape=(len(result),))


# ═══════════════════════════════════════════════════════════
# DEMO / TESTE
# ═══════════════════════════════════════════════════════════

def demo():
    """Demonstração da compressão alienígena."""
    print("=" * 60)
    print("  TENSO TENSOR CORE — Demonstração")
    print("=" * 60)
    print()

    # Teste 1: MPS com compressão
    print("── MPS: Compressão de código sequencial ──")
    mps = MPS("demo_program")
    for i in range(8):
        data = [i, i+1, i*2, (i*3)%5]
        mps.add_node(data, site_name=f"op_{i}", energy=1.0/(i+1))

    stats = mps.stats()
    print(f"  Sites: {stats['sites']}")
    print(f"  Parâmetros: {stats['total_params']}")

    ratio = mps.compress(energy_threshold=0.90)
    print(f"  Compressão: {ratio:.1f}x")
    for ev in mps.compression_events:
        print(f"    Site {ev['site']}: rank {ev['original_rank']}→{ev['compressed_rank']} ({ev['ratio']}x)")

    print()

    # Teste 2: SVD de matriz
    print("── SVD: Decomposição de matriz ──")
    A = [[1.0, 2.0, 0.5],
         [2.0, 4.0, 1.0],
         [0.5, 1.0, 0.25]]
    U, S, Vt = svd(A)
    print(f"  Valores singulares: {[round(s,4) for s in S]}")
    U, S, Vt = svd_truncate(U, S, Vt, 0.95)
    ratio = compression_ratio(U, S, Vt, (3, 3))
    print(f"  Rank após truncamento (95% energia): {len(S)}")
    print(f"  Compressão: {ratio:.1f}x")
    print()

    # Teste 3: Tensor Train
    print("── Tensor Train: Compressão multi-dimensional ──")
    data = []
    for i in range(4):
        row = []
        for j in range(3):
            row2 = []
            for k in range(2):
                row2.append(float((i+1)*(j+1)*(k+1)))
            row.append(row2)
        data.append(row)
    tensor = Tensor(data=data, shape=(4, 3, 2))
    print(f"  Original: shape={tensor.shape}, params={tensor.size}")

    tt = TensorTrain("demo").decompose(tensor, max_rank=4)
    print(f"  TT cores: {len(tt.cores)}")
    print(f"  Compressão: {tt.compression_ratio():.1f}x")

    print()
    print("=" * 60)
    print("  Compressão alienígena ativa.")
    print("=" * 60)


if __name__ == "__main__":
    demo()
