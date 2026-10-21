# ACCEPTANCE CONTRACT — MASTER PROMPT V2 (ROUND 3)
**Document:** `ACCEPTANCE_CONTRACT.md` (Version 2.1 — Frozen & Immutable by Builder)  
**System Under Test:** Hermetic MicroVM Sandbox (`F:\TITAN_HYPERION_OMEGA`)  
**Canonical Git Remote:** `https://github.com/juan3861/hermetic-microvm-sandbox`  
**Initial Baseline Commit:** `f4b54af70e8a71d2b78d655f4639e4a30a213e4b` (v2.3.0 Release)  
**Timestamp of Freeze:** 2026-10-21T17:35:00-03:00  
**Signatories:** Orquestrador, Agente 1 (The Builder), Agente 2 (The Auditor)  

---

## 1. Identificação do Workspace e Repositório Canônico
- **Caminho Canônico:** `F:\TITAN_HYPERION_OMEGA`
- **Ambiente de Execução:** Windows 11 Host + WSL2 Ubuntu Linux Kernel 5.15 + Python 3.11.9 Virtualenv (`F:\rotor-gate-venv`)
- **Espaço de Memória Volátil:** `/dev/shm` (7.8 GB tmpfs DDR5 RAM)
- **Modificações Locais Pré-Existentes:** Nenhuma (working tree 100% clean no commit baseline `f4b54af`).

---

## 2. Objetivo, Domínio, Usuários e Fronteiras de Escopo
- **Domínio:** Sandbox de altíssima performance e isolamento hermético para Agentes de IA Autônomos (AutoGPT, OpenHands, Claude Code, Devin, SWE-bench runners).
- **Usuários:** Engenheiros de IA, desenvolvedores de agentes e sistemas de orquestração autônoma.
- **Funções Obrigatórias Consolidadas:**
  1. Execução de comandos e código com confinamento hermético de hardware e de rede.
  2. Persistência de estado REPL (`run_code`) com retenção de variáveis e funções.
  3. Pre-Warmed Pool de microVMs com leasing sub-milissegundo (< 0.1 ms).
  4. Auto-cura de falhas fatais (SIGSEGV, SIGKILL/OOM, SIGABRT) via Watchdog e rollback atômico.
  5. Blindagem contra exfiltração de metadados de nuvem (`169.254.169.254`) e redes privadas RFC1918.
  6. Zero desgaste em disco físico (0 bytes gravados em NTFS).
  7. Telemetria padrão OpenMetrics/Prometheus (`/metrics`).
  8. Higienização ativa de credenciais em memória (`SecretSanitizer` com latência < 0.05 ms).
  9. Streaming contínuo de eventos tipados em tempo real (`StreamChunk`).
  10. **NOVO REQUISITO R3.1**: Terminal Pseudo-TTY Bidirecional Interativo (`SandboxPTY` / `sandbox.pty.create()`, `send_input()`, `read()`, `resize()`, `kill()`).
  11. **NOVO REQUISITO R3.2**: Motor de Rastreamento e Reprodução Determinística de Trajetória (`ReplayRecorder` / `sandbox.export_trace()`, `sandbox.replay_trace()`).
  12. **NOVO REQUISITO R3.3**: Provas Formais Z3 SMT adicionais para Não-Exfiltração de Segredos e Isolamento de Streams PTY.
- **Fronteiras Explícitas de Escopo:**
  - O projeto restringe-se estritamente ao repositório `F:\TITAN_HYPERION_OMEGA`.
  - Nenhuma modificação externa sem autorização expressa.

---

## 3. Ambiente, Arquitetura e Restrições Técnicas
- **Linguagens:** Python 3.11, C nativo (compilado via GCC -O3).
- **Camada de Isolamento:** Seccomp-BPF Ring-0, gVisor Sentry AST, Bubblewrap namespaces, MMU CoW forker, PTY POSIX terminal isolation.
- **Formato de Empacotamento:** OCI Image Spec v1.1 rootless unpacker.
- **Interfaces Públicas:**
  - Drop-in SDK: `from hermetic_sandbox import Sandbox, Process, CommandResult, StreamChunk, PTYSession`
  - CLI: `orchestrator.py` / `hermetic.cmd` / `hyperion.cmd`
  - MCP: Servidor JSON-RPC 2.0 stdio

---

## 4. Ameaças Relevantes, Licenças e Segurança
- **Ameaças Monitoradas:**
  - Fuga de terminal e manipulação de TTY escape sequences maliciosas.
  - Exfiltração de credenciais via streaming ou buffer interativo PTY.
  - SSRF contra endpoints de metadados cloud (`169.254.169.254`).
  - Indeterminismo em execuções de agentes gerando estados fantasmas.
- **Licença:** Apache 2.0 (100% permissiva, livre de contaminação GPL restritiva).

---

## 5. Baseline Reproduzível Inicial (v2.3.0 — Commit f4b54af)
- **Total de Suítes de Testes Ativas:** 21 suítes (`tests/test_*.py`).
- **Status Inicial:** 21/21 PASSED (100% GREEN, 0 falhas).
- **Latência Cold-Start (Launcher C):** 0.467 ms.
- **Latência Warm-Pool:** 0.004 ms (4 µs).
- **Desgaste de Disco Físico:** 0 bytes (verificado via `fastmft v1.3.0`).
- **Pontuação da Auditoria Anterior:** 100/100 (APPROVED).

---

## 6. Métricas de Sucesso e Critérios Eliminatórios (Tri-State Quality Gate)
Precedência Obrigatória:
1. Qualquer `FAIL` em requisito eliminatório $\rightarrow$ **REJECTED** imediato.
2. Qualquer `UNKNOWN` em requisito obrigatório $\rightarrow$ **BLOCKED** imediato.
3. Nota calculada ponderada:
   - Correção funcional e testes: 30 pontos
   - Confiabilidade e resiliência: 25 pontos
   - Segurança e confinamento: 15 pontos
   - Integração e arquitetura: 15 pontos
   - Desempenho medido: 10 pontos
   - Reprodutibilidade e documentação: 5 pontos
4. Nota < 95/100 $\rightarrow$ **REJECTED**.
5. Nota $\ge$ 95/100 + todos os requisitos obrigatórios em `PASS` $\rightarrow$ **APPROVED**.

---

## 7. Ferramentas e Autorizações
- **Python:** `F:\rotor-gate-venv\Scripts\python.exe`
- **Compilador:** `gcc` (WSL2 Ubuntu)
- **Auditor Estrito:** `F:\AetherMind_Apotheosis_Final\aethermind_apotheosis\AetherMind_Strict_Auditor.py`
- **Shell:** PowerShell e WSL2 bash.

---

## 8. Orçamento Operacional
- **Tempo:** Checkpoints curtos e iterativos.
- **Execuções:** Foco no caminho crítico do DAG.
- **Armazenamento:** Volátil em `/dev/shm`, sem resíduos no disco físico.

---

## 9. Formato Obrigatório de Evidência (Evidence Receipt)
Cada alegação de sucesso deve conter:
- Comando exato reproduzível.
- Código de retorno (`exitcode`).
- Output real do console.
- Timestamp e caminhos absolutos dos artefatos.

---

## 10. Condições de Convergência e Rollback
- Se uma alteração causar regressão ou falha de teste: isolar e corrigir a causa raiz. Se o risco superar o ganho, efetuar rollback atômico.
- Convergência atingida quando todas as lacunas forem comprovadamente resolvidas e validadas pela auditoria adversarial independente.
