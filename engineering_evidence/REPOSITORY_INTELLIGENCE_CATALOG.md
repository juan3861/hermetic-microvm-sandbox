# REPOSITORY INTELLIGENCE CATALOG — V2 SOTA DISCOVERY
**System:** Hermetic MicroVM Sandbox  
**Timestamp:** 2026-10-21T16:51:00-03:00  

---

## 1. Pesquisa Sistemática do Estado da Arte (SOTA)

### Candidato A: GitGuardian / Trufflehog / Gitleaks Secret Detection
- **Domínio:** Detecção e Redação Ativa de Segredos e Credenciais em Tempo de Execução.
- **Análise Arquitetural:** Utiliza padrões regex de alta precisão combinados com análise de entropia de Shannon para detectar chaves de API (`sk-...`, `ghp_...`, `AKIA...`, JWTs, chaves privadas PEM) sem falsos positivos excessivos.
- **Classificação:** **PRODUCTION-GRADE**
- **Decisão:** Assimilar algoritmo de redação regex + entropia em `security/secret_sanitizer.py`.

### Candidato B: E2B Streaming Protocol & OpenAI Code Interpreter Event Stream
- **Domínio:** Streaming de saída em tempo real para agentes interativos.
- **Análise Arquitetural:** Emite eventos tipados (`stdout`, `stderr`, `result`, `error`) através de geradores Python (`yield StreamChunk`), permitindo que a interface do usuário ou o modelo LLM reaja a saídas intermediárias sem bloquear a execução.
- **Classificação:** **SOTA-VERIFIED**
- **Decisão:** Integrar `run_code_stream()` e `commands.run_stream()` em `sdk/hermetic_sandbox.py`.

### Candidato C: Mutmut / Cosmic Ray (Mutation Testing Frameworks)
- **Domínio:** Verificação adversarial de sensibilidade de suítes de teste.
- **Análise Arquitetural:** Injeta mutações deliberadas no código-fonte (inversão de operadores booleanos, bypass de filtros de segurança, remoção de checagens) e verifica se a suíte de testes falha (mata o mutante). Se a suíte continuar passando, os testes possuem pontos cegos.
- **Classificação:** **SOTA-VERIFIED**
- **Decisão:** Construir gerador de mutações e verificador de morte de mutantes em `tests/test_mutation_and_invariants.py`.

---

## 2. Matriz de Seleção Justificada

| Componente | Compatibilidade (25%) | Ganho Técnico (25%) | Baixo Atrito (20%) | Maturidade (15%) | Segurança (10%) | Reversibilidade (5%) | Pontuação Total |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Secret Sanitizer** | 25 | 24 | 19 | 15 | 10 | 5 | **98 / 100** |
| **Streaming Generator** | 25 | 25 | 19 | 15 | 9 | 5 | **98 / 100** |
| **Mutation Testing Battery** | 24 | 25 | 20 | 14 | 10 | 5 | **98 / 100** |
