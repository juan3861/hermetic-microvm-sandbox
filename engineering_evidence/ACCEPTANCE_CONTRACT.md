# ACCEPTANCE CONTRACT — MASTER PROMPT V2
**Document:** `ACCEPTANCE_CONTRACT.md` (Version 2.0 — Frozen & Immutable by Builder)  
**System Under Test:** Hermetic MicroVM Sandbox (`F:\TITAN_HYPERION_OMEGA`)  
**Canonical Git Remote:** `https://github.com/juan3861/hermetic-microvm-sandbox`  
**Initial Baseline Commit:** `b27aff52be40babe73ca6f61772e8c74278d15b8`  
**Timestamp of Freeze:** 2026-10-21T16:50:00-03:00  
**Signatories:** Orquestrador, Agente 1 (The Builder), Agente 2 (The Auditor)  

---

## 1. Identificação do Workspace e Repositório Canônico
- **Caminho Canônico:** `F:\TITAN_HYPERION_OMEGA`
- **Ambiente de Execução:** Windows 11 Host + WSL2 Ubuntu Linux Kernel 5.15 + Python 3.11.9 Virtualenv (`F:\rotor-gate-venv`)
- **Espaço de Memória Volátil:** `/dev/shm` (7.8 GB tmpfs DDR5 RAM)
- **Modificações Locais Pré-Existentes:** Nenhuma (working tree 100% clean).

---

## 2. Objetivo, Domínio, Usuários e Fronteiras de Escopo
- **Domínio:** Sandbox de alta performance e isolamento hermético para Agentes de IA Autônomos (AutoGPT, OpenHands, Claude Code, Devin).
- **Usuários:** Engenheiros de IA, desenvolvedores de agentes e sistemas de orquestração autônoma.
- **Funções Obrigatórias:**
  1. Execução de comandos e código com confinamento hermético de hardware e de rede.
  2. Persistência de estado REPL (`run_code`) com retenção de variáveis e funções.
  3. Pre-Warmed Pool de microVMs com leasing sub-milissegundo (< 0.1 ms).
  4. Auto-cura de falhas fatais (SIGSEGV, SIGKILL/OOM, SIGABRT) via Watchdog e rollback atômico.
  5. Blindagem contra exfiltração de metadados de nuvem (169.254.169.254) e redes privadas RFC1918.
  6. Zero desgaste em disco físico (0 bytes gravados em NTFS).
  7. Telemetria padrão OpenMetrics/Prometheus (`/metrics`).
- **Fronteiras Explícitas de Escopo:**
  - O projeto restringe-se estritamente ao diretório `F:\TITAN_HYPERION_OMEGA`.
  - Não tocar, modificar ou alterar arquivos fora do workspace sem autorização expressa.

---

## 3. Ambiente, Arquitetura e Restrições Técnicas
- **Linguagens:** Python 3.11, C nativo (compilado via GCC -O3).
- **Camada de Isolamento:** Seccomp-BPF Ring-0, gVisor Sentry AST, Bubblewrap namespaces, MMU CoW forker.
- **Formato de Empacotamento:** OCI Image Spec v1.1 rootless unpacker.
- **Interfaces Públicas:**
  - Drop-in SDK: `from hermetic_sandbox import Sandbox, ExecutionResult`
  - CLI: `orchestrator.py` / `hermetic.cmd` / `hyperion.cmd`
  - MCP: Servidor JSON-RPC 2.0 stdio

---

## 4. Ameaças Relevantes, Licenças e Segurança
- **Ameaças Monitoradas:**
  - Fuga de container via syscalls não filtradas (`insmod`, `kexec`, `reboot`, `ptrace`).
  - SSRF contra endpoints de metadados de provedores cloud (`169.254.169.254/latest/meta-data`).
  - Ataques de exaustão de recursos (fork bombs, memory bombs, symlink traversal).
  - Vazamento de credenciais e tokens sensíveis (`sk-...`, `ghp_...`, IAM secret keys) em saídas de log.
- **Licença:** Apache 2.0. É terminantemente proibido incorporar código sob licenças incompatíveis (ex: GPL v3 estrita sem exceção).

---

## 5. Baseline Reproduzível Inicial (v2.2.0)
- **Total de Suítes de Testes Ativas:** 19 suítes (`tests/test_*.py`).
- **Status Inicial:** 19/19 PASSED (100% GREEN).
- **Latência Cold-Start (Launcher C):** 0.467 ms.
- **Latência Warm-Pool Lease:** < 0.080 ms (80 µs).
- **Desgaste em Disco Físico:** 0 bytes (NTFS MFT confirmado).
- **Contenção em Fuzzing de Syscalls:** 100/100 probes bloqueadas.

---

## 6. Métricas de Sucesso e Critérios Eliminatórios (Tri-State Quality Gate)
Todo requisito avaliado deve possuir status exclusivo: `PASS`, `FAIL` ou `UNKNOWN`.

### Precedência Obrigatória:
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
- **Tempo:** Checkpoints curtos a cada modificação.
- **Chamadas / Execuções:** Foco no caminho crítico do DAG.
- **Paralelismo:** Controlado, sem sobrecarregar a memória do host.
- **Armazenamento:** Volátil em `/dev/shm`, sem poluição do disco físico.

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
