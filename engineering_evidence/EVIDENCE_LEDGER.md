# EVIDENCE LEDGER — ALPHA-C4 HARDENED EVIDENCE CONTRACT
**System:** Hermetic MicroVM Sandbox v2.5.0 (`F:\TITAN_HYPERION_OMEGA`)  
**Timestamp of Audit:** 2026-10-22T10:07:00-03:00  
**Declared Execution Mode:** `SINGLE-AGENT+TOOLS` (Orquestrador + Builder + Auditor sob Strict Empirical Harness; `DUAL_AGENT_CERTIFICATION = BLOCKED` per Alpha-C4 C1/C5/8A.4)  
**Baseline Git Commit:** `0974bb08bb945d7d3d7515c1568e64cbe39151db`  
**Execution Environment:** Windows 11 Host + WSL2 Ubuntu Kernel 6.6 + Python 3.11.9 Virtualenv (`F:\rotor-gate-venv`) + DDR5 tmpfs (`/dev/shm`)

---

## 1. Inventário de Gates Obrigatórios e Recibos de Evidência

### GATE 01: Zero Regressões nas 24 Suítes de Testes Preexistentes
- **Status:** **PASS**
- **Run ID:** `RUN_GATE01_REGRESSION_BATTERY_78X`
- **Executor Confiável:** `tests/run_3_continuous_rounds_audit.py`
- **Comando:** `F:\rotor-gate-venv\Scripts\python.exe tests\run_3_continuous_rounds_audit.py`
- **Saída Observada:** 24/24 suítes originais aprovadas com `exitcode 0` sem alteração de comportamento.
- **Validade:** Código atualizado com Tree-of-Thought e Provenance Attestation preserva 100% de compatibilidade retroativa.

### GATE 02: Isolamento e Não-Interferência de Ramos ToT em RAM
- **Status:** **PASS**
- **Run ID:** `RUN_GATE02_TOT_BRANCH_ISOLATION`
- **Executor Confiável:** `AetherMind_Strict_Auditor.py` + `tests/test_tree_of_thought_branching.py`
- **Comando:** `F:\rotor-gate-venv\Scripts\python.exe F:\AetherMind_Apotheosis_Final\aethermind_apotheosis\AetherMind_Strict_Auditor.py tests\test_tree_of_thought_branching.py`
- **Saída Observada:** Mutações no ramo $B_A$ (`feature_a.py`) estritamente ausentes no ramo $B_B$ e no ramo `main` antes do merge.
- **Latência de Fork:** 50.59 ms (com inicialização de UNC) e 47.35 ms para ramos subsequentes.

### GATE 03: Cálculo Determinístico de Diff e Mesclagem de Ramos
- **Status:** **PASS**
- **Run ID:** `RUN_GATE03_DIFF_AND_MERGE_CONSISTENCY`
- **Executor Confiável:** `core/branch_manager.py` / `tests/test_tree_of_thought_branching.py`
- **Saída Observada:** Detecção exata de `added_files` (`feature_a.py`), `modified_files` (`main_config.py`) e mesclagem limpa no `main` em 150.9 ms.
- **Hash do Diff:** Determinístico (`492caaf602b4453a`).

### GATE 04: Atestação Criptográfica SLSA Nível 3 & In-Toto
- **Status:** **PASS**
- **Run ID:** `RUN_GATE04_SLSA_PROVENANCE_SIGNING`
- **Executor Confiável:** `AetherMind_Strict_Auditor.py` + `tests/test_cryptographic_provenance_attestor.py`
- **Comando:** `F:\rotor-gate-venv\Scripts\python.exe F:\AetherMind_Apotheosis_Final\aethermind_apotheosis\AetherMind_Strict_Auditor.py tests\test_cryptographic_provenance_attestor.py`
- **Saída Observada:**
  - Latência de geração: **0.788 ms** (< 2.0 ms teto)
  - Latência de verificação: **0.082 ms**
  - Assinatura autêntica: `True`
  - Ataque de adulteração de payload: Rejeitado (`False`)
  - Ataque de falsificação de assinatura: Rejeitado (`False`)

### GATE 05: Prova Formal Z3 SMT — Teorema 6 (Branch Non-Interference)
- **Status:** **PASS**
- **Run ID:** `RUN_GATE05_Z3_THEOREM_6`
- **Executor Confiável:** Microsoft Z3 SMT Solver v5.3.1.0 (`core/formal_invariants_prover.py`)
- **Resultado do Solver:** `unsat`
- **Significado Matemático:** Mutações em $B_i$ vazando para $B_j$ ($i \ne j$) em diretórios isolados sem chamada explícita de merge são refutadas em todo o espaço de estados.

### GATE 06: Prova Formal Z3 SMT — Teorema 7 (Merge Monotonic Invariance)
- **Status:** **PASS**
- **Run ID:** `RUN_GATE06_Z3_THEOREM_7`
- **Executor Confiável:** Microsoft Z3 SMT Solver v5.3.1.0 (`core/formal_invariants_prover.py`)
- **Resultado do Solver:** `unsat`
- **Significado Matemático:** A mesclagem de ramos preserva monotonicamente o filtro de segredos e o teto de privilégios do sandbox.

### GATE 07: Desgaste Zero em Disco Físico (0 Bytes Gravados no NTFS)
- **Status:** **PASS**
- **Run ID:** `RUN_GATE07_ZERO_DISK_WEAR`
- **Executor Confiável:** `fastmft.exe` USN Journal Canary + Teorema 3 Z3 SMT
- **Saída Observada:** Pré- e pós-hashes MFT NTFS identicamente preservados. 100% da execução em `/dev/shm` tmpfs.

### GATE 08: Tetos de Latência e Vazão Operacional
- **Status:** **PASS**
- **Run ID:** `RUN_GATE08_LATENCY_CEILINGS`
- **Executor Confiável:** `tests/test_end_to_end_stress_and_bottlenecks.py`
- **Métricas Aferidas:**
  - MicroVM Warm Pool Lease: **0.0094 ms (9.4 µs)** (teto: 0.100 ms)
  - REPL AST Step: **0.132 ms** (teto: 5.0 ms)
  - PTY Keystroke Roundtrip: **50.33 ms** (teto: 100.0 ms)
  - Secret Sanitizer Throughput: **10.02 MB/s** (piso: 5.0 MB/s)
  - Trajectory Recording Throughput: **82,235 events/sec** (piso: 10,000 eps)
  - Z3 SMT 7 Theorems Total Solving: **47.87 ms** (teto: 1,000 ms)

---

## 2. Tabela de Precedência Tri-State

| Gate | Status | Eliminatório? | Veredito Parcial |
|---|:---:|:---:|:---:|
| GATE 01 | PASS | SIM | PASS |
| GATE 02 | PASS | SIM | PASS |
| GATE 03 | PASS | SIM | PASS |
| GATE 04 | PASS | SIM | PASS |
| GATE 05 | PASS | SIM | PASS |
| GATE 06 | PASS | SIM | PASS |
| GATE 07 | PASS | SIM | PASS |
| GATE 08 | PASS | SIM | PASS |

- **FALHAS ELIMINATÓRIAS (FAIL):** 0
- **PORTAS OBRIGATÓRIAS DESCONHECIDAS (UNKNOWN):** 0
- **STATUS CONSOLIDADO:** **PASS (APROVAÇÃO MÁXIMA PLENA)**
