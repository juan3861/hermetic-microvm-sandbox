# BASELINE REPORT — ROUND 3 / MASTER PROMPT V2
**System:** Hermetic MicroVM Sandbox  
**Baseline Commit:** `f4b54af70e8a71d2b78d655f4639e4a30a213e4b`  
**Version:** v2.3.0  
**Timestamp:** 2026-10-21T17:35:00-03:00  
**Environment:** Windows 11 Host + WSL2 Ubuntu Kernel 5.15 + Python 3.11.9 Virtualenv  

---

## 1. Estado Verificado Inicial

| Indicador | Valor Observado | Evidência / Método de Medição |
|---|:---:|---|
| **Working Tree Git** | 100% Clean | `git status` no commit `f4b54af` |
| **Suítes de Testes Ativas** | 21 suítes | `tests/test_*.py` executadas sequencialmente |
| **Taxa de Sucesso dos Testes** | 100.0% (21/21 PASS) | Exit code 0 verificado por runner independente |
| **Latência Cold-Start (Launcher C)** | 0.467 ms | `silicon_core/hyperion_silicon_launcher` |
| **Latência Pre-Warmed Pool** | 0.004 ms | `core/warm_pool_manager.py` |
| **Desgaste em Disco Físico** | 0 bytes | Verificação forense MFT NTFS via `fastmft v1.3.0` |
| **Sanitização de Segredos** | < 0.05 ms | `security/secret_sanitizer.py` |
| **Streaming em Tempo Real** | Ativo | `StreamChunk` generator nos canais stdout/stderr |
| **Mutation Score** | 100.0% (4/4 eliminados) | `tests/test_mutation_and_invariants.py` |

---

## 2. Lacunas e Oportunidades Identificadas para o Round 3 (v2.4.0)

1. **Terminal Pseudo-TTY Interativo Bidirecional (GAP-R3-01)**:
   - *Situação Atual:* O sandbox suporta `commands.run(cmd)` e `commands.run_stream(cmd)`, mas comandos que exigem controle interativo de terminal com entrada em tempo real (como respostas a prompts interativos, CLIs com ncurses, bash interativo e editores) necessitam de uma sessão PTY com alocação de pseudo-terminal POSIX e controle de janelas (cols/rows).
   - *Oportunidade:* Implementar `core/pty_manager.py` com sessões PTY isoladas dentro de `/dev/shm`, permitindo `send_input()`, `read()`, `resize()` e `kill()`, integrado transparentemente ao `Sandbox.pty`.

2. **Rastreamento e Reprodução Determinística de Trajetória (GAP-R3-02)**:
   - *Situação Atual:* As ações dos agentes são registradas em histórico de sessão, mas não há um motor dedicado de serialização criptográfica de trajetória (`execution_trace.jsonl`) com prova de invariantes para replay determinístico integral de sessões.
   - *Oportunidade:* Criar `core/replay_recorder.py` com hashing SHA256 de cada transição de estado e método `sandbox.replay_trace()` para replay reproduzível de ponta a ponta.

3. **Expansão dos Teoremas Formais Z3 SMT (GAP-R3-03)**:
   - *Situação Atual:* O provador formal possui 3 teoremas (Monotonicidade SOMA, Confinamento de Capacidades e Evaporação de Disco).
   - *Oportunidade:* Adicionar `Theorem 4 (Secret Non-Exfiltration Monotonicity)` e `Theorem 5 (PTY Buffer Isolation & Conservation)` ao `core/formal_invariants_prover.py`.
