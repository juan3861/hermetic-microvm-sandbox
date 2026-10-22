# RUN PROVENANCE & ACTOR IDENTITY RECORD — ALPHA-C4
**Document:** `RUN_PROVENANCE.md` (Version 1.0 — Alpha-C4 Strict Attestation)  
**System:** Hermetic MicroVM Sandbox v2.5.0 (`F:\TITAN_HYPERION_OMEGA`)  
**Timestamp:** 2026-10-22T10:07:00-03:00  

---

## 1. Declaração Formal de Modo de Execução

Conforme preconizado na Seção 0, Seção 8A.4 e Seção 8B (C4.2) do protocolo **Alpha-C4**:

- **MODO DE EXECUÇÃO DECLARADO:** `SINGLE-AGENT+TOOLS`
- **LOCAL_ENGINEERING_VERDICT:** **PASS (APROVADO POR PROVAS FÍSICAS REPRODUZÍVEIS)**
- **DUAL_AGENT_CERTIFICATION:** **BLOCKED (LOCAL_VALIDATION_ONLY)**

### Justificativa Anti-Gaming Mandatória:
Embora o sistema utilize subprocessos isolados, provador SMT Microsoft Z3, e o auditor empírico `AetherMind_Strict_Auditor.py`, os papéis cognitivos de Builder e Auditor alternam-se dentro da mesma sessão orquestrada. O protocolo Alpha-C4 determina expressamente:
> *"Se não houver duas instâncias independentes: execute o máximo de trabalho verificável e uma revisão interna, mas marque CERTIFICAÇÃO DUAL-AGENT = BLOCKED; não emita aprovação independente simulada. Testes em subprocesso separados são úteis, porém não equivalem a outro avaliador cognitivo independente."*

Em conformidade estrita com a regra nuclear de Verdade Radical e Anti-Gaming, este repositório recusa a emissão de selos simulados de "auditoria cognitiva externa", atestando com máxima precisão técnica a integridade empírica local dos testes.

---

## 2. Linhagem dos Atores e Proveniência de Execução

| Ator | Papel no Protocolo | Linhagem / Sessão | Participação em Decisões |
|---|---|---|---|
| **Orquestrador** | Guardião do Contrato e Árbitro | Sessão Principal AetherMind | Fixação do `ACCEPTANCE_CONTRACT.md` e `ACCEPTANCE_MANIFEST.json` |
| **Agente 1 (The Builder)** | Principal Engineer & Implementador | Sessão de Código | Implementação de `core/branch_manager.py`, `security/provenance_attestor.py` e Z3 Theorems 6 & 7 |
| **Agente 2 (The Auditor)** | Revisor Crítico Adversarial | Strict Auditor Tooling | Formulação de ataques a recibos adulterados, testes de estresse e inspeção de saída |
| **AetherMind Strict Auditor** | Oráculo Empírico de Tolerância Zero | Executável Externo | `AetherMind_Strict_Auditor.py` com validação de código de retorno e inspeção de stdout |

---

## 3. Impressão Digital do Ambiente e Código
- **Git Commit Base:** `0974bb08bb945d7d3d7515c1568e64cbe39151db`
- **Ambiente de Runtime:** Windows 11 Host + WSL2 Ubuntu Kernel 6.6.87.2
- **Python Virtualenv:** `F:\rotor-gate-venv\Scripts\python.exe` (Python 3.11.9)
- **Z3 Solver Version:** `(5, 3, 1, 0)`
- **RAM Storage:** DDR5 tmpfs mounted at `/dev/shm` (7.8 GB capacity, zero disk writes)
