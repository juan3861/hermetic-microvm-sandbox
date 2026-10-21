# COMPONENT REUSE MANIFEST — MASTER PROMPT V2
**System:** Hermetic MicroVM Sandbox v2.3.0  
**Timestamp:** 2026-10-21T16:51:00-03:00  

---

## 1. Relação de Peças Selecionadas e Estratégia de Encaixe

1. **`security/secret_sanitizer.py` (SecretSanitizer)**:
   - **Origem:** Padrões TruffleHog / GitGuardian adaptados para streaming em Python.
   - **Estratégia de Integração:** Wrapper / Filter aplicado automaticamente a saídas de shell e do interpretador REPL.
   - **Licença:** Apache 2.0 compatível.
   - **Critério de Aceitação:** Interceptar e mascarar chaves OpenAI (`sk-...`), GitHub (`ghp_...`), AWS (`AKIA...`), Slack tokens, e chaves privadas RSA/EC sem corromper texto legítimo.

2. **`sdk/hermetic_sandbox.py` (Streaming Execution Conduit)**:
   - **Origem:** E2B / OpenHands streaming generator protocol.
   - **Estratégia de Integração:** Drop-in extension na classe `Sandbox`.
   - **Critério de Aceitação:** `sandbox.run_code_stream()` emite objetos `StreamChunk` de forma contínua durante a execução.

3. **`tests/test_mutation_and_invariants.py` (Adversarial Mutation & Invariant Suite)**:
   - **Origem:** Princípios Mutmut / Metamorphic Testing.
   - **Estratégia de Integração:** Suíte de teste independente adicionada ao diretório `tests/`.
   - **Critério de Aceitação:** 100% dos mutantes artificiais injetados em filtros de segurança devem ser mortos (detectados e rejeitados) pelos testes.
