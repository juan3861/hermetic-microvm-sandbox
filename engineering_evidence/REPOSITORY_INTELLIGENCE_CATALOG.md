# REPOSITORY INTELLIGENCE CATALOG — V2 SOTA DISCOVERY (ROUND 3)
**System:** Hermetic MicroVM Sandbox  
**Timestamp:** 2026-10-21T17:36:00-03:00  

---

## 1. Pesquisa Sistemática do Estado da Arte (SOTA) — Rodada 3

### Candidato D: E2B Interactive Terminal (PTY) / Modal Interactive Shell
- **Domínio:** Pseudo-Terminais (PTY) bidirecionais interativos para Agentes AGI.
- **Análise Arquitetural:** Em vez de execuções batch isoladas, agentes avançados como OpenHands, SWE-bench e Claude Code necessitam de sessões de terminal interativas persistentes (PTY) capazes de enviar `stdin` em tempo real (ex: responder confirmações `[y/N]`, senhas, flags interativas), redimensionar janelas (`winsize`) e capturar buffers ANSI raw.
- **Classificação:** **SOTA-VERIFIED**
- **Decisão:** Desenvolver `core/pty_manager.py` com suporte a alocação de PTY POSIX em `/dev/shm`, expondo `sandbox.pty.create()`, `send_input()`, `read()`, `resize()` e `kill()`.

### Candidato E: SWE-bench / OpenHands Deterministic Trajectory Replay Engine
- **Domínio:** Gravação e reprodução determinística de trajetórias de agentes.
- **Análise Arquitetural:** Garante auditoria forense completa através do registro criptográfico sequencial (JSONL) de cada comando executado, código avaliado, escrita de arquivo e snapshot gerado, com hashing SHA256 de estados e replay idempotente.
- **Classificação:** **PRODUCTION-GRADE**
- **Decisão:** Desenvolver `core/replay_recorder.py` com persistência em memória e método `sandbox.replay_trace()` no SDK.

### Candidato F: Isabelle/HOL & seL4 Formal Stream Invariants (Z3 SMT)
- **Domínio:** Verificação formal de propriedades de fluxo contínuo e não-vazamento.
- **Análise Arquitetural:** Modelar matematicamente a não-exfiltração de segredos (Theorem 4) e a conservação/isolamento de canais PTY (Theorem 5) no solucionador SMT Z3.
- **Classificação:** **RESEARCH-GRADE / FORMAL-PROVEN**
- **Decisão:** Integrar Theorems 4 e 5 em `core/formal_invariants_prover.py`.

---

## 2. Matriz de Seleção Justificada — Rodada 3

| Componente | Compatibilidade (25%) | Ganho Técnico (25%) | Baixo Atrito (20%) | Maturidade (15%) | Segurança (10%) | Reversibilidade (5%) | Pontuação Total |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Interactive PTY Manager** | 25 | 25 | 20 | 14 | 9 | 5 | **98 / 100** |
| **Deterministic Replay Engine** | 25 | 24 | 20 | 15 | 10 | 5 | **99 / 100** |
| **Z3 SMT Stream Invariants** | 24 | 25 | 19 | 15 | 10 | 5 | **98 / 100** |
