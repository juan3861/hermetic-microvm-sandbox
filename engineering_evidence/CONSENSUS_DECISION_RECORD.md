# CONSENSUS DECISION RECORD — PROTOCOLO ALPHA-C (DECISION C4-01)
**Decision ID:** `DECISION-C4-01-TOT-BRANCHING-AND-PROVENANCE`  
**Timestamp:** 2026-10-22T09:19:00-03:00  
**Baseline Commit:** `0974bb08bb945d7d3d7515c1568e64cbe39151db`  
**Activation Reason:** Escolha arquitetural e priorização dos pilares do Salto v2.5.0 entre Tree-of-Thought Branching, SLSA Provenance Attestation e Virtual Clock Time-Warp.  
**Operational Arrangement:** MODO PREFERENCIAL (Agente 1 gera Lente AGI e Lente ASI; Agente 2 audita e contesta independentemente).

---

## 1. Alternativas Concretas Avaliadas

| Alternativa | Descrição | Benefício Imediato | Risco Sistêmico / Longo Prazo | Esforço |
|---|---|---|---|:---:|
| **Alt A: ToT Branching & RAM Diff/Merge** | Ramificação de estado em `/dev/shm`, cálculo de diff de arquivos/AST e merge atômico. | Permite busca em árvore (ToT/MCTS) em microsegundos sem reiniciar VMs. | Risco de colisão de arquivos ou vazamento entre ramos concorrentes se mal isolados. | Médio |
| **Alt B: SLSA In-Toto Provenance Attestation** | Geração de envelope de proveniência criptográfico assinado com digest SHA-256 e chave efêmera. | Verificação de integridade para swarms de múltiplos agentes; previne resultados forjados. | Sobrecarga de latência na geração de chaves/assinaturas se não otimizado em RAM. | Baixo |
| **Alt C: Virtual Clock Time-Warp** | Aceleração de tempo virtual via `LD_PRELOAD` ou ptrace para eliminar delays em testes. | Testes com `sleep()` executam instantaneamente. | **Alto atrito:** Incompatibilidade com Seccomp-BPF Ring-0 e Landlock LSM que bloqueiam `LD_PRELOAD`/ptrace. | Alto |

---

## 2. Pareceres das Lentes Analíticas

### 2.1. Lente AGI (Curto Prazo, Execução, Integração, Recursos)
- **Posição:** Priorizar Alt A (ToT Branching) e Alt B (SLSA Provenance).
- **Justificativa:** Entregam valor prático imediato para pipelines de agentes (SWE-bench / OpenHands / Claude Code).
- **Crítica de Alt C:** Tentar injetar relógio virtual com `LD_PRELOAD` quebra o confinamento estrito do Silicon Core (`hyperion_seccomp_bpf`). O custo de engenharia é desproporcional ao benefício.
- **Menor Experimento Discriminatório:** Testar se o `BranchManager` em `/dev/shm` atinge latência < 1.0 ms para fork e switch de ramos.

### 2.2. Lente ASI (Efeitos Sistêmicos, Longo Prazo, Riscos, Escalabilidade)
- **Posição:** Aprovar Alt A e Alt B sob a condição inegociável de validação matemática formal de não-interferência e conservação.
- **Justificativa:** Em sistemas de execução especulativa em árvore, se um ramo $B_1$ puder vazar mutações para $B_2$, toda a integridade da inferência é corrompida.
- **Exigência Sistêmica:** O `BranchManager` e a mesclagem devem ser acompanhados por dois novos Teoremas Formais Z3 SMT:
  - *Teorema 6*: Não-interferência absoluta entre ramos de memória volátil.
  - *Teorema 7*: Monotonicidade da higienização de segredos durante a mesclagem.

---

## 3. Rodada de Contestação Disciplinada

1. **Agente 1 (Builder) contesta o risco sistêmico de Alt A:**
   - O risco de colisão de arquivos em `/dev/shm` é mitigado encapsulando cada ramo em um subdiretório isolado `/dev/shm/branches/<branch_id>/` com links simbólicos somente-leitura para o estado base até a primeira mutação (Copy-on-Write em espaço de usuário).
2. **Agente 2 (Auditor) contesta o custo de oportunidade do excesso de cautela:**
   - Adiar Alt C (Virtual Clock) é tecnicamente justificado para evitar conflito com Ring-0 Seccomp-BPF. A auditoria focará em tentar quebrar o isolamento de ramos da Alt A e testar a validade das assinaturas criptográficas da Alt B.

---

## 4. Decisão Consolidada do Orquestrador
- **Veredito:** **AGREED (COMBINAR ALT A + ALT B + TEOREMAS Z3 6 E 7)**
- **Próximos Passos Atômicos:**
  1. Implementar `core/branch_manager.py` (Task T1)
  2. Implementar `security/provenance_attestor.py` (Task T2)
  3. Formular e provar Teoremas 6 e 7 em `core/formal_invariants_prover.py` (Task T3)
  4. Integrar ao SDK `hermetic_sandbox.py` e CLI `orchestrator.py` (Task T4)
  5. Criar suítes de teste de estresse e refutação adversarial (Task T5)
- **Critério de Rollback:** Se o fork de ramo ultrapassar 2.0 ms ou se qualquer teorema Z3 retornar `sat` (violando a segurança formal), abortar e reverter.
