# EXECUTION ROADMAP & DAG — MASTER PROMPT V2
**System:** Hermetic MicroVM Sandbox v2.3.0  
**Timestamp:** 2026-10-21T16:51:00-03:00  

---

## 1. Directed Acyclic Graph (DAG) de Implementação

```mermaid
flowchart TD
    T0["Freeze Acceptance Contract (ACCEPTANCE_CONTRACT.md)"] --> T1["Implement SecretSanitizer (security/secret_sanitizer.py)"]
    T1 --> T2["Integrate Secret Sanitizer in REPL & Sandbox SDK"]
    T0 --> T3["Implement Streaming Generator (sdk/hermetic_sandbox.py)"]
    T2 & T3 --> T4["Update orchestrator.py CLI & Telemetry"]
    T4 --> T5["Build Mutation & Invariant Test Suite (test_mutation_and_invariants.py)"]
    T5 --> T6["Build Secret Sanitizer Test Suite (test_secret_sanitizer.py)"]
    T6 --> T7["Batch Regression Test (All 21 Suites)"]
    T7 --> T8["Strict Auditor Certification (AetherMind_Strict_Auditor.py)"]
    T8 --> T9["Independent Adversarial Audit by Subagent"]
    T9 --> T10["Final Acceptance, Commit & Push"]
```

---

## 2. Caminho Crítico e Priorização
- **P0 (Crítico):** `security/secret_sanitizer.py` (Prevenção de vazamento de credenciais).
- **P1 (Funcional):** Streaming generator em `sdk/hermetic_sandbox.py`.
- **P2 (Adversarial):** Bateria de testes de mutação e invariantes.
- **P3 (Auditoria):** Execução independente pelo subagente e veredito do auditor.
