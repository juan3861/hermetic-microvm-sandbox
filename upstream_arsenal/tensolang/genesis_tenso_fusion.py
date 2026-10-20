"""
╔══════════════════════════════════════════════════════════╗
║  GENESIS + TENSO = LINGUAGEM QUE EVOLUI                ║
║  v2 — com dados reais de alta redundância              ║
╚══════════════════════════════════════════════════════════╝
"""
import sys, os, time, json, math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import tensor_core as tc

class GenesisTensorFusion:
    def __init__(self):
        self.generations = []
        self.evolved_code = ""

    def evolve(self, tensors_definition, max_iterations=3):
        """
        Recebe uma definição de tensores e evolui comprimindo.
        Cada iteração: comprime → avalia → regenera com rank menor.
        """
        print("╔══════════════════════════════════════════════════════════╗")
        print("║  GENESIS + TENSO FUSION — EVOLUÇÃO INICIADA            ║")
        print("║  Dados com redundância → compressão REAL               ║")
        print("╚══════════════════════════════════════════════════════════╝")
        print()

        current = tensors_definition  # list of dicts: {name, data, shape_hint}
        total_compression = 1.0
        all_events = []

        for gen in range(max_iterations):
            print(f"═══ ITERAÇÃO {gen + 1}/{max_iterations} ═══")
            t0 = time.time()

            gen_ratios = []
            gen_ranks = []
            next_generation = []

            for tdef in current:
                name = tdef['name']
                data = tdef['data']

                # Constrói tensor a partir dos dados
                if isinstance(data[0], list):
                    # Já é 2D
                    tensor = tc.Tensor.from_list(data)
                else:
                    # 1D → reshape para 2D (guess shape)
                    n = len(data)
                    cols = min(int(math.sqrt(n)) + 1, n)
                    rows = (n + cols - 1) // cols
                    padded = data + [0.0] * (rows * cols - n)
                    matrix = [padded[i*cols:(i+1)*cols] for i in range(rows)]
                    tensor = tc.Tensor.from_list(matrix)

                original_params = tensor.size
                mat = tensor.to_matrix()

                # SVD + truncamento com energia progressivamente menor
                energy = max(0.60, 0.95 - gen * 0.10)  # Começa em 95%, desce até 60%
                U, S, Vt = tc.svd(mat)
                U, S, Vt = tc.svd_truncate(U, S, Vt, energy_threshold=energy)

                ratio = tc.compression_ratio(U, S, Vt, (len(mat), len(mat[0]) if mat else 0))
                new_rank = len(S)

                gen_ratios.append(ratio)
                gen_ranks.append(new_rank)

                # Reconstrói a partir do SVD truncado
                # U (m×r) × diag(S) (r×r) × Vt (r×n) = matriz comprimida (m×n)
                compressed_matrix = []
                for i in range(len(U)):
                    row = []
                    for j in range(len(Vt[0]) if Vt else 0):
                        val = sum(U[i][k] * S[k] * Vt[k][j] for k in range(new_rank))
                        row.append(round(val, 4))
                    compressed_matrix.append(row)

                # Prepara para próxima iteração
                next_generation.append({
                    'name': f"{name}_g{gen+1}",
                    'data': compressed_matrix,
                    'shape_hint': (len(compressed_matrix), len(compressed_matrix[0]) if compressed_matrix else 0)
                })

                all_events.append({
                    'gen': gen + 1,
                    'name': name,
                    'original_params': original_params,
                    'compressed_rank': new_rank,
                    'ratio': round(ratio, 3),
                    'energy': energy
                })

                print(f"  [{name}] {tensor.shape} → rank {new_rank} | {ratio:.2f}x | energy={energy*100:.0f}%")

            avg_ratio = sum(gen_ratios) / len(gen_ratios) if gen_ratios else 1.0
            total_compression *= avg_ratio
            dt = (time.time() - t0) * 1000

            self.generations.append({
                'gen': gen + 1,
                'avg_ratio': round(avg_ratio, 3),
                'cumulative': round(total_compression, 3),
                'ranks': gen_ranks,
                'time_ms': round(dt, 1),
                'energy': max(0.60, 0.95 - gen * 0.10)
            })

            print(f"  → Média: {avg_ratio:.2f}x | Acumulada: {total_compression:.2f}x | {dt:.1f}ms")
            print()

            current = next_generation

            if avg_ratio <= 1.01 and gen >= 1:
                print("  ⟲ Convergência — compressão estabilizou")
                break

        # ─── RELATÓRIO ───
        print("═" * 65)
        print("  RELATÓRIO — GENESIS+TENSO: A LINGUAGEM QUE EVOLUI")
        print("═" * 65)
        for g in self.generations:
            bar = "█" * max(1, int(g['avg_ratio'] * 5))
            ranks = g['ranks']
            print(f"  Gen {g['gen']}: {g['avg_ratio']:.2f}x {bar}")
            print(f"         ranks={ranks} | energy={g['energy']*100:.0f}% | {g['time_ms']}ms")

        print(f"\n  Compressão acumulada: {total_compression:.2f}x")

        # dE/dt
        if len(self.generations) >= 2:
            r0 = self.generations[0]['avg_ratio']
            rn = self.generations[-1]['avg_ratio']
            dedt = (total_compression - 1.0) / len(self.generations)
        else:
            dedt = 0

        mu, lam, S = 0.03, 0.01, 1.5
        survival = (mu * S * total_compression - lam)
        print(f"\n  Equação Mestra: dE/dt = (μ×S×U - λ) × E")
        print(f"  U = {total_compression:.2f} | dE/dt = {survival:.4f}")
        print(f"  Status: {'🟢 VIVO — evolui' if survival > 0 else '🔴 ESTAGNADO'}")

        # Bônus: código GenesisLang equivalente comprimido
        print(f"\n  CÓDIGO GENESIS GERADO (após compressão):")
        final = current[0] if current else {}
        print(f"  // {final.get('name', 'tensor')}: {final.get('shape_hint', (0,0))}")
        print(f"  // Representação comprimida — rank latente")

        return {
            'generations': self.generations,
            'total_compression': total_compression,
            'dE_dt': dedt,
            'U': total_compression,
            'events': all_events
        }


# ═══════════════════════════════════════════════════════════
# DADOS REAIS DE ALTA REDUNDÂNCIA
# ═══════════════════════════════════════════════════════════

def generate_signal_matrix(n_samples=100, n_channels=5):
    """Gera matriz de sinais com estrutura de baixo rank (senoides)."""
    import math
    matrix = []
    for ch in range(n_channels):
        freq = 1.0 + ch * 0.5
        phase = ch * math.pi / 4
        row = [math.sin(2 * math.pi * freq * i / n_samples + phase) for i in range(n_samples)]
        matrix.append(row)
    return matrix

def generate_correlation_matrix(n=15):
    """Matriz de correlação com blocos (altamente comprimível)."""
    import math
    mat = []
    for i in range(n):
        row = []
        for j in range(n):
            # Blocos de correlação: grupos de 3-4 conceitos correlacionados
            block_i = i // 4
            block_j = j // 4
            if block_i == block_j:
                val = 0.7 + 0.3 * (1 - abs(i - j) / 4.0)
            else:
                val = 0.1 * math.exp(-abs(block_i - block_j))
            row.append(round(val, 3))
        mat.append(row)
    return mat

def generate_activation_matrix(n_concepts=20, n_modules=10):
    """Matriz de ativação conceitos×módulos (esparsa + blocos)."""
    import random
    random.seed(42)
    mat = []
    for c in range(n_concepts):
        row = []
        for m in range(n_modules):
            # Cada conceito ativa 2-3 módulos com intensidade alta
            if m in [(c * 3) % n_modules, (c * 3 + 1) % n_modules, (c * 3 + 2) % n_modules]:
                val = random.uniform(0.7, 1.0)
            else:
                val = random.uniform(0.0, 0.15)
            row.append(round(val, 3))
        mat.append(row)
    return mat


if __name__ == "__main__":
    print("Gerando dados de alta redundância...")
    print()

    # Dataset 1: Sinais de 5 canais × 100 amostras (altamente redundante — senoides)
    signals = generate_signal_matrix(n_samples=100, n_channels=5)

    # Dataset 2: Matriz de correlação 15×15 (blocos)
    corr = generate_correlation_matrix(15)

    # Dataset 3: Ativação 20×10 (esparsa + blocos)
    activations = generate_activation_matrix(20, 10)

    tensors = [
        {'name': 'signals', 'data': signals},
        {'name': 'correlation', 'data': corr},
        {'name': 'activations', 'data': activations},
    ]

    fusion = GenesisTensorFusion()
    result = fusion.evolve(tensors, max_iterations=4)

    print(f"\n═══ EVENTOS DETALHADOS ═══")
    for e in result['events']:
        print(f"  Gen{e['gen']} | {e['name']:15s} | {e['original_params']:4d}→rank{e['compressed_rank']:2d} | {e['ratio']:.2f}x | @{e['energy']*100:.0f}%")
