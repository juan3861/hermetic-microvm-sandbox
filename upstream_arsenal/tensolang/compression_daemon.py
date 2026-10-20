"""
╔══════════════════════════════════════════════════════════════╗
║  AETHERMIND SELF-COMPRESSION DAEMON                        ║
║  A AGI que comprime a si mesma — continuamente             ║
║  Genesis + Tenso fusion em loop vivo                       ║
║  Fibonacci rhythms: 2Hz → 1Hz → 0.33Hz → 0.125Hz          ║
╚══════════════════════════════════════════════════════════════╝
"""
import os, sys, time, json, math, gc, random
from pathlib import Path
from datetime import datetime
from collections import deque

# ─── CONFIG ────────────────────────────────────────────────
AETHERMIND_ROOT = Path("F:/AetherMind_Apotheosis_Final/aethermind_core")
VAULT_ROOT = Path("F:/AetherMind_Vault")
TENSOLANG_DIR = Path(__file__).parent
STATE_FILE = TENSOLANG_DIR / "compression_state.json"
LOG_FILE = TENSOLANG_DIR / "compression_daemon.log"

sys.path.insert(0, str(TENSOLANG_DIR))
import tensor_core as tc

# ─── FIBONACCI SCHEDULER ───────────────────────────────────
FIB_RHYTHMS = [0.5, 1.0, 3.0, 8.0, 14.0]

class FibonacciScheduler:
    def __init__(self):
        self.rhythm_index = 0
        self.cycle_count = 0

    def next_interval(self):
        self.cycle_count += 1
        if self.cycle_count % 5 == 0 and self.rhythm_index < len(FIB_RHYTHMS) - 1:
            self.rhythm_index += 1
        return FIB_RHYTHMS[self.rhythm_index]

    def rhythm_name(self):
        return f"{FIB_RHYTHMS[self.rhythm_index]}s (idx={self.rhythm_index})"


class ResourceMonitor:
    @staticmethod
    def get_state():
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory()
            return {'cpu_percent': cpu, 'ram_free_gb': round(mem.available / (1024**3), 1),
                    'ram_total_gb': round(mem.total / (1024**3), 1)}
        except ImportError:
            return {'cpu_percent': 50, 'ram_free_gb': 4, 'ram_total_gb': 34}

    @staticmethod
    def can_work_hard():
        s = ResourceMonitor.get_state()
        return s['cpu_percent'] < 70 and s['ram_free_gb'] > 1.0

    @staticmethod
    def can_work_normal():
        s = ResourceMonitor.get_state()
        return s['cpu_percent'] < 85 and s['ram_free_gb'] > 0.5


class AetherMindSensor:
    def scan(self):
        tensors = []
        try:
            tensors.extend(self._scan_modules())
        except: pass
        try:
            tensors.extend(self._scan_vault())
        except: pass
        try:
            tensors.extend(self._scan_memory())
        except: pass
        return tensors

    def _scan_modules(self):
        tensors = []
        module_dirs = [
            AETHERMIND_ROOT / "01_percepcao",
            AETHERMIND_ROOT / "02_memoria",
            AETHERMIND_ROOT / "03_raciocinio",
            AETHERMIND_ROOT / "04_planejamento",
            AETHERMIND_ROOT / "05_governanca",
        ]
        module_sizes = []
        for d in module_dirs:
            if d.exists():
                try:
                    count = 0
                    total_size = 0
                    for f in list(d.iterdir())[:30]:
                        if f.is_file() and f.suffix == '.py':
                            count += 1
                            try: total_size += f.stat().st_size
                            except: pass
                    module_sizes.append({'dir': d.name, 'size_kb': round(total_size / 1024, 1), 'files': count})
                except: pass
        if module_sizes:
            data = []
            for m in module_sizes:
                complexity = min(1.0, m['files'] / 20.0)
                data.append([m['size_kb'] / 100.0, m['files'] / 10.0, complexity])
            if len(data) >= 3:
                tensors.append({'name': 'psi_modules', 'data': data, 'metadata': module_sizes, 'source': 'modules_scan'})
        return tensors

    def _scan_vault(self):
        tensors = []
        if VAULT_ROOT.exists():
            try:
                trunk_stats = {}
                # Scan rápido: apenas 2 níveis, ignora .obsidian
                for item in list(VAULT_ROOT.iterdir())[:20]:
                    if item.is_dir() and not item.name.startswith('.'):
                        count = 0
                        total_size = 0
                        for sub in list(item.iterdir())[:200]:
                            if sub.is_file() and sub.suffix == '.md':
                                count += 1
                                try: total_size += sub.stat().st_size
                                except: pass
                        if count > 0:
                            trunk_stats[item.name] = {'files': count, 'size_kb': round(total_size / 1024, 1)}
            except: return tensors
            if trunk_stats:
                data = []
                for name, stats in sorted(trunk_stats.items()):
                    data.append([stats['files'], stats['size_kb'] / 10.0])
                if len(data) >= 3:
                    tensors.append({'name': 'vault_knowledge', 'data': data, 'metadata': trunk_stats, 'source': 'vault_scan'})
        return tensors

    def _scan_memory(self):
        tensors = []
        task_cortex = Path("F:/AetherMind_Vault/task_cortex.json")
        if task_cortex.exists():
            try:
                tasks = json.loads(task_cortex.read_text())
                if isinstance(tasks, dict) and 'tasks' in tasks:
                    task_list = tasks['tasks']
                    status_counts = {'pending': 0, 'in_progress': 0, 'completed': 0, 'cancelled': 0}
                    for t in task_list:
                        s = t.get('status', 'pending')
                        status_counts[s] = status_counts.get(s, 0) + 1
                    data = [[status_counts.get(s, 0), i/10.0] for i, s in enumerate(['pending', 'in_progress', 'completed', 'cancelled'])]
                    tensors.append({'name': 'task_cortex_state', 'data': data, 'metadata': status_counts, 'source': 'memory_scan'})
            except: pass
        return tensors


class TensorCompressor:
    def __init__(self):
        self.history = deque(maxlen=100)

    def compress(self, tensor_def, energy=0.85):
        data = tensor_def['data']
        name = tensor_def['name']
        try:
            if isinstance(data[0], list):
                tensor = tc.Tensor.from_list(data)
            else:
                n = len(data)
                cols = min(int(math.sqrt(n)) + 1, n)
                rows = (n + cols - 1) // cols
                padded = data + [0.0] * (rows * cols - n)
                matrix = [padded[i*cols:(i+1)*cols] for i in range(rows)]
                tensor = tc.Tensor.from_list(matrix)
            original_params = tensor.size
            mat = tensor.to_matrix()
            U, S, Vt = tc.svd(mat)
            U, S, Vt = tc.svd_truncate(U, S, Vt, energy_threshold=energy)
            ratio = tc.compression_ratio(U, S, Vt, (len(mat), len(mat[0]) if mat else 0))
            return {'name': name, 'original_params': original_params, 'compressed_rank': len(S),
                    'ratio': round(ratio, 3), 'energy': energy,
                    'singular_values': [round(s, 4) for s in S[:5]], 'compressed': True}
        except Exception as e:
            return {'name': name, 'error': str(e), 'ratio': 1.0, 'compressed': False}


class StateRegenerator:
    def apply(self, compression_results, generation):
        ratios = [r['ratio'] for r in compression_results if r.get('compressed')]
        product = 1.0
        for r in ratios: product *= r
        state = {'generation': generation, 'timestamp': datetime.now().isoformat(),
                 'compressions': compression_results, 'total_ratio': round(product, 3)}
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state, indent=2))
        log_entry = {'gen': generation, 'time': state['timestamp'], 'ratio': state['total_ratio'],
                     'tensors': len(compression_results),
                     'ranks': [r.get('compressed_rank', 0) for r in compression_results]}
        with open(LOG_FILE, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        return state


class SelfCompressionDaemon:
    def __init__(self):
        self.sensor = AetherMindSensor()
        self.compressor = TensorCompressor()
        self.regenerator = StateRegenerator()
        self.scheduler = FibonacciScheduler()
        self.monitor = ResourceMonitor()
        self.generation = 0
        self.total_compression = 1.0
        self.running = True

    def tick(self):
        self.generation += 1
        t0 = time.time()
        tensors = self.sensor.scan()
        if not tensors:
            return None
        energy = max(0.60, 0.95 - self.generation * 0.02)
        results = []
        for t in tensors:
            r = self.compressor.compress(t, energy=energy)
            results.append(r)
        state = self.regenerator.apply(results, self.generation)
        dt = (time.time() - t0) * 1000
        self.total_compression *= state['total_ratio']
        return {**state, 'time_ms': round(dt, 1),
                'cumulative_ratio': round(self.total_compression, 3),
                'energy': energy, 'tensors_found': len(tensors)}

    def run(self, max_generations=None):
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║  AETHERMIND SELF-COMPRESSION DAEMON — ATIVADO             ║")
        print("║  A AGI comprime a si mesma. Loop infinito.                ║")
        print("╚══════════════════════════════════════════════════════════════╝\n")
        gen = 0
        while self.running:
            gen += 1
            if max_generations and gen > max_generations:
                break
            if not self.monitor.can_work_normal():
                print(f"  [gen {gen}] Recursos baixos — pausando 15s")
                time.sleep(15)
                continue
            result = self.tick()
            interval = self.scheduler.next_interval()
            if result:
                ranks = [r.get('compressed_rank', '?') for r in result.get('compressions', [])]
                ratio = result['total_ratio']
                bar = "█" * max(1, int(ratio * 5))
                print(f"  Gen {result['generation']:3d} | {ratio:.2f}x {bar} | ranks={ranks} | {result['time_ms']:.0f}ms | next={interval}s")
            time.sleep(interval)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="AetherMind Self-Compression Daemon")
    p.add_argument("action", nargs="?", default="run", choices=["run", "once", "status", "log"])
    p.add_argument("--gens", type=int, default=None)
    args = p.parse_args()

    if args.action == "status":
        if STATE_FILE.exists():
            state = json.loads(STATE_FILE.read_text())
            print(f"Última compressão: Gen {state['generation']} | {state['timestamp']}")
            print(f"Ratio: {state['total_ratio']}x")
            for c in state.get('compressions', []):
                print(f"  [{c['name']}] {c.get('original_params', '?')}→rank{c.get('compressed_rank', '?')} | {c.get('ratio', '?')}x")
        else:
            print("Nenhum estado encontrado.")
    elif args.action == "log":
        if LOG_FILE.exists():
            for line in LOG_FILE.read_text().strip().split('\n')[-20:]:
                e = json.loads(line)
                print(f"  Gen {e['gen']:3d} | {e['ratio']:.2f}x | ranks={e['ranks']} | {e['time']}")
        else:
            print("Log vazio.")
    elif args.action == "once":
        daemon = SelfCompressionDaemon()
        result = daemon.tick()
        if result:
            print(json.dumps(result, indent=2, default=str))
        else:
            print("Nenhum tensor encontrado.")
    else:
        daemon = SelfCompressionDaemon()
        try:
            daemon.run(max_generations=args.gens)
        except KeyboardInterrupt:
            print(f"\n\nDaemon interrompido. {daemon.generation} gerações, {daemon.total_compression:.2f}x acumulado.")
