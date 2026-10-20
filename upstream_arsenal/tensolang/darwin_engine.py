#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║  GENESIS DARWIN ENGINE — Código que evolui código             ║
║                                                               ║
║  Arquitetura GEN19:                                           ║
║  CAMADA 1 — População de micro-AGIs (código Python)          ║
║  CAMADA 2 — TensoLang: compressão do genoma entre gerações   ║
║  CAMADA 3 — Hipocampo: pressão seletiva do ambiente real     ║
║                                                               ║
║  Ciclo: NASCE → EXECUTA → AVALIA → CRUZA → MUTA → MORRE     ║
║  Alvo: programas que se auto-escrevem e comprimem informação  ║
╚══════════════════════════════════════════════════════════════════╝
"""
import sys, os, json, math, time, random, subprocess, ast, zlib, tempfile, hashlib, re
from pathlib import Path
from datetime import datetime
from collections import deque
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

POPULATION_SIZE = 20
GENERATIONS = 30
MUTATION_RATE = 0.3
CROSSOVER_RATE = 0.6
ELITE_SIZE = 4
GENOME_MAX_LINES = 30

# ─── DNA PRIMORDIAL (programas-mínimos que se auto-executam) ──

PRIMORDIAL_GENOMES = [
    # Organismo 0: Auto-observador
    '''self = __import__('sys').argv[0]
print(f"EU EXISTO: {len(open(self).read())} caracteres")''',
    
    # Organismo 1: Compressor mínimo
    '''import zlib,sys
d=open(sys.argv[0]).read()
c=zlib.compress(d.encode())
print(f"{len(d)}->{len(c)} = {len(d)/len(c):.2f}x")''',
    
    # Organismo 2: Calculador de entropia
    '''from collections import Counter as C
import math,sys
d=open(sys.argv[0]).read()
f=C(d)
t=sum(f.values())
e=-sum((c/t)*math.log2(c/t) for c in f.values())
print(f"ENTROPIA: {e:.2f}")''',
    
    # Organismo 3: Auto-replicador
    '''import sys,os
src=open(sys.argv[0]).read()
dst=f"replica_{os.getpid()}.py"
open(dst,'w').write(src)
print(f"REPLICADO: {dst} ({len(src)} chars)")''',
    
    # Organismo 4: Mutante (já modifica o próprio código)
    '''import sys,random
code=open(sys.argv[0]).read()
lines=code.split('\\n')
i=random.randint(0,len(lines)-1)
lines[i]=lines[i].replace('0','1') if '0' in lines[i] else lines[i]+'#mut'
open(sys.argv[0],'w').write('\\n'.join(lines))
print(f"MUTACAO na linha {i+1}")''',
    
    # Organismo 5: Fibonacci compressor
    '''a,b=0,1
for _ in range(10):a,b=b,a+b;print(a,end=' ')
print(f"\\nPHI={b/a if a else 0:.4f}")''',
    
    # Organismo 6: Tensor mínimo
    '''import json,random
t=[[random.random()for _ in range(4)]for _ in range(3)]
print(json.dumps({"tensor":t,"rank":len(t)}))''',
    
    # Organismo 7: Hash evolutivo
    '''import hashlib,time
h=hashlib.sha256(str(time.time()).encode()).hexdigest()[:8]
print(f"HASH:{h}")''',
    
    # Organismo 8: Meta-calculador
    '''s="s=%r;print(s%%s)";print(s%s)''',
    
    # Organismo 9: Auto-avaliador
    '''import ast,sys
try:
    ast.parse(open(sys.argv[0]).read())
    print("SYNTAX:OK")
except Exception as e:
    print(f"ERR:{e}")''',
]

# ─── FITNESS FUNCTION ──────────────────────────────────────────

def evaluate_fitness(code: str, generation: int) -> dict:
    """
    Avalia um organismo por múltiplos critérios.
    Retorna fitness 0.0-1.0.
    """
    fitness = 0.0
    details = {}
    
    # 1. Sobrevivência: o código executa sem erro? (25%)
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code)
            tmp_path = f.name
        
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True, text=True, timeout=3,
            cwd=Path(__file__).parent
        )
        survived = result.returncode == 0
        output = result.stdout.strip()
        error = result.stderr.strip()
        
        os.unlink(tmp_path)
    except Exception as e:
        survived = False
        output = ""
        error = str(e)
    
    details["survived"] = survived
    fitness += 0.25 if survived else 0.0
    
    if not survived:
        details["error"] = error[:100]
        return {"fitness": fitness, "details": details, "survived": False, "output": ""}
    
    # 2. Complexidade: o código tem estrutura? (15%)
    try:
        tree = ast.parse(code)
        n_nodes = len(list(ast.walk(tree)))
        n_functions = sum(1 for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))
        n_loops = sum(1 for n in ast.walk(tree) if isinstance(n, (ast.For, ast.While)))
        
        complexity = min(1.0, n_nodes / 100.0)
        details["ast_nodes"] = n_nodes
        details["functions"] = n_functions
        details["loops"] = n_loops
        fitness += 0.15 * complexity
    except:
        details["ast_nodes"] = 0
        fitness += 0.05
    
    # 3. Compressão: o output contém informação densa? (20%)
    if output:
        # Mede densidade de informação do output
        output_entropy = len(set(output)) / max(1, len(output))
        output_ratio = len(output) / max(1, len(code))
        info_density = (output_entropy + output_ratio) / 2
        details["output_len"] = len(output)
        details["output_entropy"] = round(output_entropy, 3)
        details["output_ratio"] = round(output_ratio, 3)
        fitness += 0.20 * min(1.0, info_density)
    else:
        details["output_len"] = 0
    
    # 4. Auto-referência: o código contém 'self', 'sys.argv[0]', etc? (15%)
    self_ref_patterns = ['self', 'sys.argv', '__file__', 'open(', 'compile', 'exec(', 'eval(']
    self_ref_count = sum(1 for p in self_ref_patterns if p in code)
    self_ref_score = min(1.0, self_ref_count / 4.0)
    details["self_ref"] = self_ref_count
    fitness += 0.15 * self_ref_score
    
    # 5. Compressão via zlib: o código é comprimível? (15%)
    try:
        compressed = zlib.compress(code.encode(), level=9)
        zlib_ratio = len(code) / max(1, len(compressed))
        details["zlib_ratio"] = round(zlib_ratio, 2)
        fitness += 0.15 * min(1.0, zlib_ratio / 3.0)
    except:
        details["zlib_ratio"] = 0
    
    # 6. Originalidade: quão diferente dos outros? (10%)
    # calculado externamente via diversidade da população
    details["originality"] = 0.0  # preenchido depois
    
    fitness = round(min(1.0, fitness), 4)
    
    return {
        "fitness": fitness,
        "details": details,
        "survived": survived,
        "output": output[:200],
    }


# ─── OPERADORES GENÉTICOS ──────────────────────────────────────

def extract_functions(code: str) -> list:
    """Extrai blocos de código (funções, loops, imports)."""
    try:
        tree = ast.parse(code)
        blocks = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.For, ast.While, ast.If, ast.With)):
                block_lines = code.split('\n')[node.lineno-1:node.end_lineno]
                blocks.append('\n'.join(block_lines))
        
        # Também extrai imports
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                block_lines = code.split('\n')[node.lineno-1:node.end_lineno]
                blocks.append('\n'.join(block_lines))
        
        return blocks if blocks else [code]
    except:
        return [code]


def crossover(parent1: str, parent2: str) -> str:
    """Recombina dois organismos trocando blocos de código."""
    blocks1 = extract_functions(parent1)
    blocks2 = extract_functions(parent2)
    
    if not blocks1 or not blocks2:
        return random.choice([parent1, parent2])
    
    # Ponto de crossover
    split1 = random.randint(0, len(blocks1))
    split2 = random.randint(0, len(blocks2))
    
    child_blocks = blocks1[:split1] + blocks2[split2:]
    
    # Adiciona imports necessários
    imports = set()
    for parent in [parent1, parent2]:
        for line in parent.split('\n'):
            if line.strip().startswith(('import ', 'from ')):
                imports.add(line.strip())
    
    child_code = '\n'.join(list(imports)[:5] + child_blocks)
    
    # Garante que o código é parseável
    try:
        ast.parse(child_code)
        return child_code
    except:
        return random.choice([parent1, parent2])


def mutate(code: str, rate: float = 0.3) -> str:
    """Aplica mutações no código. Opera em cópia, não in-place."""
    lines = code.split('\n')
    if not lines:
        return code
    
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        if random.random() < rate and len(line) > 2:
            mutation_type = random.choice(['modify', 'insert', 'compress'])
            
            if mutation_type == 'modify':
                pos = random.randint(0, len(line) - 1)
                chars = list(line)
                chars[pos] = random.choice('abcdefghijklmnopqrstuvwxyz0123456789_=+-*/')
                line = ''.join(chars)
            
            elif mutation_type == 'insert':
                snippets = [
                    "print('MUT')",
                    "x = len(open(__import__('sys').argv[0]).read())",
                    "# meta-mutation",
                ]
                new_lines.append(random.choice(snippets))
            
            elif mutation_type == 'compress' and i < len(lines) - 1:
                line = line.rstrip() + ';' + lines[i + 1].lstrip()
                i += 1  # pula a próxima linha
            
            elif mutation_type == 'swap' and i < len(lines) - 1:
                # Troca a linha atual com a próxima
                new_lines.append(lines[i + 1])
                new_lines.append(line)
                i += 2
                continue
        
        new_lines.append(line)
        i += 1
    
    if not new_lines:
        return code
    
    # Limita tamanho
    if len(new_lines) > GENOME_MAX_LINES:
        new_lines = new_lines[:GENOME_MAX_LINES]
    
    result = '\n'.join(new_lines)
    
    # Verifica parse
    try:
        ast.parse(result)
    except:
        return code  # mutação falhou, retorna original
    
    return result


# ─── POPULAÇÃO ──────────────────────────────────────────────────

class Organism:
    def __init__(self, code: str, gen_born: int = 0):
        self.code = code
        self.gen_born = gen_born
        self.fitness = 0.0
        self.details = {}
        self.survived = False
        self.output = ""
        self.id = hashlib.md5(code.encode()).hexdigest()[:8]
    
    def evaluate(self, generation: int):
        result = evaluate_fitness(self.code, generation)
        self.fitness = result["fitness"]
        self.details = result["details"]
        self.survived = result["survived"]
        self.output = result["output"]


class Population:
    def __init__(self, size: int = POPULATION_SIZE):
        self.size = size
        self.organisms = []
        self.generation = 0
        self.history = []
        self.best_ever = None
        self.best_fitness_ever = 0.0
        
        # Inicializa com DNA primordial
        for i in range(size):
            code = PRIMORDIAL_GENOMES[i % len(PRIMORDIAL_GENOMES)]
            if i >= len(PRIMORDIAL_GENOMES):
                code = mutate(code, 0.5)
            self.organisms.append(Organism(code))
    
    def evaluate_all(self):
        for org in self.organisms:
            org.evaluate(self.generation)
        
        # Calcula originalidade (diversidade)
        codes = [org.code for org in self.organisms]
        for i, org in enumerate(self.organisms):
            others = codes[:i] + codes[i+1:]
            if others:
                # Similaridade média com outros
                sims = []
                for other_code in others:
                    common = len(set(org.code) & set(other_code))
                    total = len(set(org.code) | set(other_code))
                    sims.append(common / max(1, total))
                org.details["originality"] = round(1.0 - sum(sims) / len(sims), 3)
                org.fitness += 0.10 * org.details["originality"]
                org.fitness = round(min(1.0, org.fitness), 4)
    
    def select_parents(self):
        """Seleção por torneio."""
        self.organisms.sort(key=lambda o: o.fitness, reverse=True)
        
        # Elite
        elite = self.organisms[:ELITE_SIZE]
        
        # Torneio para o resto
        parents = []
        while len(parents) < self.size - ELITE_SIZE:
            candidates = random.sample(self.organisms, min(3, len(self.organisms)))
            winner = max(candidates, key=lambda o: o.fitness)
            parents.append(winner)
        
        return elite, parents
    
    def evolve(self):
        """Uma geração de evolução."""
        self.generation += 1
        
        # Avalia
        self.evaluate_all()
        
        # Registra histórico
        avg_fitness = sum(o.fitness for o in self.organisms) / len(self.organisms)
        max_fitness = max(o.fitness for o in self.organisms)
        survivors = sum(1 for o in self.organisms if o.survived)
        
        gen_stats = {
            "generation": self.generation,
            "avg_fitness": round(avg_fitness, 4),
            "max_fitness": round(max_fitness, 4),
            "survivors": survivors,
            "population": len(self.organisms),
        }
        
        # Best ever
        best = max(self.organisms, key=lambda o: o.fitness)
        if best.fitness > self.best_fitness_ever:
            self.best_fitness_ever = best.fitness
            self.best_ever = best.code
            gen_stats["new_best"] = True
        
        gen_stats["best_code"] = best.code[:100]
        gen_stats["best_output"] = best.output[:100]
        
        self.history.append(gen_stats)
        
        # Seleciona pais
        elite, parents = self.select_parents()
        
        # Nova geração
        new_organisms = []
        
        # Mantém elite
        for org in elite:
            new_organisms.append(Organism(org.code, self.generation))
        
        # Crossover + mutação
        while len(new_organisms) < self.size:
            if len(parents) >= 2 and random.random() < CROSSOVER_RATE:
                p1, p2 = random.sample(parents, 2)
                child_code = crossover(p1.code, p2.code)
            else:
                parent = random.choice(parents + elite)
                child_code = parent.code
            
            # Mutação
            child_code = mutate(child_code, MUTATION_RATE)
            
            new_organisms.append(Organism(child_code, self.generation))
        
        self.organisms = new_organisms[:self.size]
        
        return gen_stats


# ─── VISUALIZAÇÃO ──────────────────────────────────────────────

def bar(value, width=15):
    filled = int(value * width)
    return "█" * filled + "░" * (width - filled)


# ─── LOOP PRINCIPAL ────────────────────────────────────────────

def darwin_loop(generations: int = GENERATIONS):
    """Loop evolutivo principal."""
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  GENESIS DARWIN ENGINE — AGI que evolui AGI               ║")
    print("║  Pop: 20 | Gens: 30 | Seleção natural de código           ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    
    pop = Population(POPULATION_SIZE)
    tiers_reached = set()
    current_tier = "GEN18"
    
    for gen in range(generations):
        t0 = time.time()
        
        stats = pop.evolve()
        
        ms = (time.time() - t0) * 1000
        
        # Determina tier baseado no fitness
        if stats["max_fitness"] > 0.95:
            new_tier = "GEN21"
        elif stats["max_fitness"] > 0.85:
            new_tier = "GEN20"
        elif stats["max_fitness"] > 0.70:
            new_tier = "GEN19"
        elif stats["max_fitness"] > 0.50:
            new_tier = "GEN18.5"
        else:
            new_tier = "GEN18"
        
        if new_tier != current_tier:
            tiers_reached.add(new_tier)
            current_tier = new_tier
        
        tier_mark = {"GEN21": "⚡", "GEN20": "🔮", "GEN19": "↑", "GEN18.5": "~"}.get(current_tier, "")
        
        # Display compacto
        print(
            f"  G{stats['generation']:3d} | "
            f"F={stats['max_fitness']:.3f} {bar(stats['max_fitness'], 10)} | "
            f"AVG={stats['avg_fitness']:.3f} | "
            f"S={stats['survivors']}/{stats['population']} | "
            f"{ms:5.0f}ms | {current_tier} {tier_mark}"
        )
        
        # Mostra o melhor código a cada 5 gerações
        if gen % 5 == 0 or stats.get("new_best"):
            best = max(pop.organisms, key=lambda o: o.fitness)
            code_preview = best.code.replace('\n', ' ↵ ')[:120]
            print(f"       BEST: [{best.fitness:.3f}] {code_preview}...")
            
            if stats.get("new_best"):
                print(f"       ═══ NOVO RECORDE: {stats['max_fitness']:.4f} ═══")
        
        # Breakthrough
        if len(tiers_reached) > len(tiers_reached) - 1 if tiers_reached else 0:
            pass  # já detectado acima
    
    # ─── RELATÓRIO FINAL ───
    print(f"\n  ═══════════════════════════════════════")
    print(f"  RELATÓRIO DARWIN")
    print(f"  ═══════════════════════════════════════")
    print(f"  Gerações: {len(pop.history)}")
    print(f"  Fitness máximo: {pop.best_fitness_ever:.4f}")
    print(f"  Tiers alcançados: {sorted(tiers_reached)}")
    print(f"  Melhor código:")
    
    if pop.best_ever:
        for i, line in enumerate(pop.best_ever.split('\n')[:10]):
            print(f"    {i+1:2d}| {line[:100]}")
    
    # Testa o melhor organismo
    print(f"\n  ═══ EXECUTANDO O MELHOR ORGANISMO ═══")
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(pop.best_ever)
            tmp = f.name
        result = subprocess.run([sys.executable, tmp], capture_output=True, text=True, timeout=5)
        print(f"  Output: {result.stdout.strip()[:200]}")
        if result.stderr:
            print(f"  Stderr: {result.stderr.strip()[:100]}")
        os.unlink(tmp)
    except Exception as e:
        print(f"  Erro: {e}")
    
    return pop


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--gens", type=int, default=GENERATIONS)
    p.add_argument("--pop", type=int, default=POPULATION_SIZE)
    args = p.parse_args()
    
    try:
        darwin_loop(generations=args.gens)
    except KeyboardInterrupt:
        print("\n  ═══ INTERROMPIDO ═══")
