# COMPONENT REUSE MANIFEST — ROUND 3
**System:** Hermetic MicroVM Sandbox  
**Timestamp:** 2026-10-21T17:36:00-03:00  

---

## 1. Princípio do Reuso em Primeiro Lugar (Reuse-First Hierarchy)

Hierarquia mandatória aplicada:
1. Padrões POSIX nativos do Kernel (`openpty`, `termios`, `winsize` via Python `pty`/`termios` e WSL2).
2. Algoritmos de ordenação e hashing determinístico criptográfico (SHA256, JSONL padronizado).
3. Microsoft Z3 SMT Theorem Prover (formal unsat refutation).

---

## 2. Componentes Selecionados e Licenciamento

| ID | Componente Reutilizado / Integrado | Origem & Padrão | Licença | Justificativa de Engenharia |
|---|---|---|:---:|---|
| C-01 | **POSIX OpenPTY Subsystem** | Linux Kernel 5.15 / POSIX PTY | Nativo | Permite alocação instantânea de pseudo-terminais sem daemons adicionais. |
| C-02 | **OpenHands / SWE-bench Trajectory Model** | OpenHands / SWE-bench Specification | MIT / Apache 2.0 | Formato universal de serialização de trajetórias para agentes de código. |
| C-03 | **Z3 SMT Invariant Verification** | Microsoft Z3 Theorem Prover | MIT | Provas matemáticas de não-violação de segurança em tempo de compilação/teste. |

---

## 3. Conformidade e Segurança da Cadeia de Suprimentos
- Zero dependências proprietárias ou fechadas adicionadas.
- Todas as dependências externas operam no ambiente virtual já homologado (`F:\rotor-gate-venv`).
