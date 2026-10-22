# ACCEPTANCE CONTRACT — MASTER PROMPT ALPHA-C4
**Document:** `ACCEPTANCE_CONTRACT.md` (Version 3.0 — Alpha-C4 Frozen & Immutable Contract)  
**System Under Test:** Hermetic MicroVM Sandbox (`F:\TITAN_HYPERION_OMEGA`)  
**Canonical Git Remote:** `https://github.com/juan3861/hermetic-microvm-sandbox`  
**Initial Baseline Commit:** `0974bb08bb945d7d3d7515c1568e64cbe39151db` (v2.4.0 Final Synchronized Release)  
**Timestamp of Freeze:** 2026-10-22T09:15:00-03:00  
**Declared Execution Mode:** `SINGLE-AGENT+TOOLS` (Orquestrador + Builder + Auditor operando sobre o harness de auditoria empírica estrita `AetherMind_Strict_Auditor.py`; `DUAL_AGENT_CERTIFICATION = BLOCKED` conforme diretriz anti-gaming Alpha-C4 C1/C5/8A.4)  
**Signatories:** Orquestrador, Agente 1 (The Builder), Agente 2 (The Auditor)

---

## 1. Identificação do Workspace e Repositório Canônico
- **Caminho Canônico:** `F:\TITAN_HYPERION_OMEGA`
- **Ambiente de Execução:** Windows 11 Host + WSL2 Ubuntu Linux Kernel 6.6 + Python 3.11.9 Virtualenv (`F:\rotor-gate-venv`)
- **Espaço de Memória Volátil:** `/dev/shm` (7.8 GB tmpfs DDR5 RAM)
- **Modificações Locais Pré-Existentes:** Nenhuma (working tree 100% clean no commit baseline `0974bb0`).

---

## 2. Objetivo, Domínio, Usuários e Fronteiras de Escopo
- **Domínio:** Sandbox de altíssima performance e isolamento hermético para Agentes de IA Autônomos (AutoGPT, OpenHands, Claude Code, Devin, SWE-bench runners, Tree-of-Thought search swarms).
- **Usuários:** Engenheiros de IA, desenvolvedores de agentes e sistemas de orquestração autônoma.
- **Funções Obrigatórias Consolidadas (v2.4.0 Baseline):**
  1. Execução de comandos e código com confinamento hermético de hardware e de rede (`bwrap`, Seccomp-BPF Ring-0).
  2. Persistência de estado REPL (`run_code`) com retenção de variáveis e funções em RAM.
  3. Pre-Warmed Pool de microVMs com leasing sub-milissegundo (< 0.01 ms / 9 µs).
  4. Auto-cura de falhas fatais (SIGSEGV, SIGKILL/OOM, SIGABRT) via Watchdog e rollback atômico.
  5. Blindagem contra exfiltração de metadados de nuvem (`169.254.169.254`) e redes privadas RFC1918.
  6. Zero desgaste em disco físico (0 bytes gravados em NTFS comprovados via `fastmft.exe`).
  7. Telemetria padrão OpenMetrics/Prometheus (`/metrics`).
  8. Higienização ativa de credenciais em memória (`SecretSanitizer` com throughput de 10.7 MB/s).
  9. Streaming contínuo de eventos tipados em tempo real (`StreamChunk`).
  10. Terminal Pseudo-TTY Bidirecional Interativo (`SandboxPTY` / `sandbox.pty.create()`).
  11. Motor de Rastreamento e Reprodução Determinística de Trajetória (`ReplayRecorder` / `ReplayEngine`).
  12. Provas Formais Z3 SMT (5 Teoremas comprovados `unsat`).

- **Novos Requisitos Mandatórios para v2.5.0 (Alpha-C4 Apex):**
  13. **REQUISITO R4.1 — Tree-of-Thought (ToT) Branching & Dynamic Memory Diff/Merge**:
      - Capacidade de ramificar o estado volátil da sandbox em múltiplos ramos nomeados (`sandbox.fork_branch("search_b1")`).
      - Alternância atômica entre ramos em RAM (`sandbox.switch_branch("search_b1")`).
      - Cálculo de diferencial exato de estado entre ramos (`sandbox.diff_branches("main", "search_b1") -> MemoryBranchDiff`), catalogando arquivos criados, modificados, deletados e deltas de variáveis no REPL AST.
      - Mesclagem atômica de ramos (`sandbox.merge_branch("search_b1", strategy="fast-forward|three-way")`) sem persistência em disco host.
  14. **REQUISITO R4.2 — Cryptographic Provenance Attestation (SLSA Level 3 & In-Toto Supply Chain)**:
      - Motor de atestação criptográfica de execução (`security/provenance_attestor.py` / `sandbox.attest_execution()`).
      - Geração de recibos de proveniência formato In-Toto / SLSA v1.0 assinados com chave efêmera Ed25519/HMAC gerada em DDR RAM.
      - Inclusão de digests criptográficos (SHA-256) do código executado, saída stdout/stderr, ambiente de kernel, filtros de seccomp e timestamp com monotonicidade estrita.
  15. **REQUISITO R4.3 — Provas Formais Z3 SMT: Teoremas 6 e 7**:
      - *Teorema 6 (Branch Non-Interference)*: Prova matemática via Z3 SMT de que mutações em ramo $B_i$ não afetam o estado do ramo $B_j$ ($i \ne j$) antes da mesclagem explícita (`unsat`).
      - *Teorema 7 (Merge Monotonic Invariance)*: Prova matemática via Z3 SMT de que a mesclagem de ramos preserva invariantes de higienização de credenciais e confinamento de privilégios (`unsat`).

- **Fronteiras Explícitas de Escopo:**
  - O projeto restringe-se estritamente ao repositório `F:\TITAN_HYPERION_OMEGA`.
  - Nenhuma modificação externa sem autorização expressa.

---

## 3. Ambiente, Arquitetura e Restrições Técnicas
- **Linguagens:** Python 3.11, C nativo (compilado via GCC -O3).
- **Camada de Isolamento:** Seccomp-BPF Ring-0, gVisor Sentry AST, Bubblewrap namespaces, MMU CoW forker, PTY POSIX terminal isolation.
- **Formato de Empacotamento:** OCI Image Spec v1.1 rootless unpacker.
- **Interfaces Públicas:**
  - Drop-in SDK: `from hermetic_sandbox import Sandbox, HermeticSandbox, Process, CommandResult, StreamChunk, PTYSession, ReplayRecorder, ReplayEngine, BranchManager, MemoryBranchDiff, ExecutionProvenanceReceipt`
  - CLI: `orchestrator.py` / `hermetic.cmd` / `hyperion.cmd`
  - MCP: Servidor JSON-RPC 2.0 stdio

---

## 4. Ameaças Relevantes, Licenças e Segurança
- **Ameaças Monitoradas:**
  - Contaminação cruzada de memória entre ramos concorrentes em Tree-of-Thought search.
  - Falsificação de recibos de execução em swarms de múltiplos agentes.
  - Exfiltração de credenciais via diferencial de ramos ou payloads de mesclagem.
  - Fuga de terminal e manipulação de TTY escape sequences maliciosas.
  - SSRF contra endpoints de metadados cloud (`169.254.169.254`).
- **Licença:** Apache 2.0 (100% permissiva, livre de contaminação GPL restritiva).

---

## 5. Baseline de Funcionalidade, Desempenho e Recursos
- **Baseline de Testes:** 24 suítes de testes 100% aprovadas em 3 rodadas consecutivas (commit `0974bb0`).
- **Baseline de Desempenho:**
  - Silicon Native C Launcher: 0.558 ms
  - MicroVM Warm Pool Lease: 0.009 ms (9 µs)
  - MMU CoW Rollback: 1.83 µs
  - Secret Sanitizer Throughput: 10.69 MB/s
  - Desgaste em disco host NTFS: 0 bytes

---

## 6. Métricas de Sucesso, Tolerâncias e Critérios Eliminatórios
- **Critérios Eliminatórios (FAIL):**
  1. Qualquer vazamento de arquivo ou escrita no NTFS durante operações de branching e mesclagem (tolerância: 0 bytes).
  2. Qualquer falha de integridade em que ramo $B_i$ modifique silenciosamente dados do ramo $B_j$.
  3. Falha na geração ou validação da assinatura criptográfica do recibo de proveniência In-Toto / SLSA.
  4. Qualquer contraexemplo encontrado pelo Z3 SMT para os Teoremas 6 e 7 (deve ser `unsat`).
  5. Qualquer regressão nas 24 suítes de testes preexistentes.
- **Critérios de Desempenho:**
  - Operação de fork de ramo em RAM: < 1.0 ms
  - Geração de recibo de proveniência SLSA: < 2.0 ms
  - Resolução dos Teoremas 6 e 7 no Z3 SMT: < 50.0 ms

---

## 7. Tri-State Quality Gate & Pesos Congelados (Protocolo Alpha-C4)
$$\text{Precedência Obrigatória: } \text{FAIL} \longrightarrow \text{UNKNOWN} \longrightarrow \text{Score} \ge 95$$

| Dimensão de Engenharia | Peso Congelado | Limiar Mínimo |
| :--- | :---: | :---: |
| **1. Correção Funcional e Testes** | 30 | 30 |
| **2. Confiabilidade e Resiliência** | 25 | 25 |
| **3. Segurança e Confinamento** | 15 | 15 |
| **4. Arquitetura e Integração** | 15 | 15 |
| **5. Desempenho Medido** | 10 | 10 |
| **6. Reprodutibilidade e Telemetria** | 5 | 5 |
| **TOTAL** | **100** | **95** |

- **LOCAL_ENGINEERING_VERDICT**: Avaliado objetivamente por ferramentas confiáveis (`AetherMind_Strict_Auditor.py`, `pytest`, `z3`).
- **DUAL_AGENT_CERTIFICATION**: Declarado como `BLOCKED` (ou `LOCAL_VALIDATION_ONLY`), preservando a verdade radical e a regra anti-gaming Alpha-C4.

---

## 8. Hipóteses Refutáveis
- **Hipótese H1:** O gerenciador de ramos em RAM (`BranchManager`) consegue criar, alternar e mesclar ramos em `/dev/shm` com tempo de execução inferior a 1.0 ms e zero mutação no NTFS.
- **Hipótese H2:** O motor de proveniência criptográfica (`ProvenanceAttestor`) gera atestações no padrão SLSA/In-Toto com assinaturas verificáveis por oráculo independente, adicionando latência inferior a 2.0 ms.
- **Hipótese H3:** Os Teoremas 6 e 7 formulados no Z3 SMT provam matematicamente (`unsat`) a não-interferência entre ramos e a invariância monótona de higienização de segredos em mesclagens.
- **Hipótese H4:** A expansão para 26+ suítes de testes roda sem nenhuma regressão nas suítes 01 a 24.
