# SCOPE & ACCEPTANCE CONTRACT (ALPHA-C7 DISCOVERY-100)
**Protocol Edition:** Alpha-C7 Discovery-100 (v4.0)  
**Repository Canonical Path:** `F:\TITAN_HYPERION_OMEGA`  
**Git Base Commit:** `829877b46d060576b04faa574f9a8a1dbe9353e9`  
**Remote Origin:** `https://github.com/juan3861/hermetic-microvm-sandbox.git`  
**Execution Transparency Mode:** `SINGLE_AGENT_WITH_TOOLS` (Rule 0 / Anti-Gaming Mandatory Declaration)  
**External Ledger Status:** `UNAVAILABLE` (Local Hash-Chain Ledger Active)  
**Contract Version Hash:** SHA-256 computed on frozen state  

---

## 1. Objetivo Supremo e Fronteiras de Escopo
- **Missão:** Elevar o `Hermetic MicroVM Sandbox` ao ápice de engenharia open source através de descoberta sistemática Discovery-100 (100 repositórios catalogados), reutilização modular de engrenagens de ponta (Tracee/IOVisor eBPF telemetry model e Sigstore Rekor transparency integration), expansão de teoremas formais Z3 SMT (Teorema 8 de Reversibilidade Monotônica) e validação adversarial ininterrupta.
- **Fronteira Explícita:**
  - O projeto é estritamente confinado ao repositório local e a dependências oficiais open source.
  - Zero desgaste de disco host no NTFS durante a execução (`0 bytes`, verificado por `fastmft.exe`).
  - Nenhuma simulação cognitiva independente quando operando sob um único modelo (Audit Verdict: `LOCAL_ENGINEERING_VERDICT = APPROVED`, `DUAL_AGENT_CERTIFICATION = BLOCKED (LOCAL_VALIDATION_ONLY)`).

---

## 2. Requisitos Funcionais e Não-Funcionais (IDs Únicos)
- **[REQ-C7-1] Discovery-100 Catalog:** Catalogação sistemática de 100 repositórios reais, canônicos e únicos no nicho de sandboxing, runtimes para agentes, eBPF, verificação formal e proveniência criptográfica (`DISCOVERY_100_CATALOG.csv`).
- **[REQ-C7-2] Component Scorecard:** Avaliação de engrenagens candidatas nos eixos Relevância (0-100) e Prontidão (0-100), com limiar de staging $\ge 80$.
- **[REQ-C7-3] Kernel eBPF Telemetry Ring-Buffer:** Monitoramento comportamental em RAM de chamadas de sistema (syscalls) e anomalias de execução sem overhead de rede (`security/behavioral_ebpf_monitor.py`).
- **[REQ-C7-4] Sigstore Rekor Transparency Log Integration:** Geração de entradas criptográficas Rekor v0.0.1 (HashedRekord) para envelopes In-Toto / DSSE offline sem chamadas de rede externas (`security/provenance_attestor.py`).
- **[REQ-C7-5] Formal SMT Theorem 8 (State Checkpoint Reversibility):** Prova matemática irrefutável via Microsoft Z3 SMT demonstrando que o rollback de estado de memória restaura identicamente o estado original sem vazamento entrópico (`core/formal_invariants_prover.py`).
- **[REQ-C7-6] Expansão da Bateria de Testes:** Ampliação para 27 suítes de teste mestras com zero regressões funcionais.
- **[REQ-C7-7] Certificação de 3 Rodadas Consecutivas:** Execução de 3 ciclos completos ininterruptos sem falhas, gargalos ou mutações de disco host.
- **[REQ-C7-8] Rastreabilidade de Evidências Alpha-C6/C7:** Geração de `AUDIT_LEDGER_ROOT.json`, `EVIDENCE_LEDGER.md` e hashes criptográficos vinculados.

---

## 3. Critérios Eliminatórios (FAIL Conditions)
1. **Host NTFS Mutation**: Qualquer escrita detectada no NTFS de `F:\` durante execução de sandbox (tolerância: 0 bytes).
2. **Fabricação de Dados no Discovery-100**: Presença de URLs inventadas, repositórios inexistentes ou forks contados como distintos sem justificativa (reprovação sumária).
3. **Falsificação de Independência**: Declarar `DUAL_AGENT_VERIFIED` quando a execução ocorre em sessão única (`SINGLE_AGENT_WITH_TOOLS`).
4. **Regressão Funcional**: Falha em qualquer uma das 26 suítes preexistentes.
5. **Violação de Teorema SMT**: Qualquer contraexemplo gerado pelo Z3 SMT para os Teoremas 1 a 8 (`sat` = FAIL).

---

## 4. Matriz de Pesos Congelados (Rubrica Alpha-C7)
$$\text{Precedência Obrigatória: } \text{FAIL} \longrightarrow \text{UNKNOWN} \longrightarrow \text{Score} \ge 95$$

| Dimensão de Engenharia | Peso Congelado | Limiar de Aprovação | Status |
| :--- | :---: | :---: | :---: |
| **1. Correção Funcional & Testes** | 25 | 25 | PENDENTE |
| **2. Confinamento, Isolamento & Zero Wear** | 20 | 20 | PENDENTE |
| **3. Descoberta Discovery-100 & Reuso Modular**| 20 | 20 | PENDENTE |
| **4. Desempenho Medido & Latência Sub-ms** | 15 | 15 | PENDENTE |
| **5. Verificação Matemática Z3 (8 Teoremas)**| 10 | 10 | PENDENTE |
| **6. Governança, Proveniência & Evidências** | 10 | 10 | PENDENTE |
| **TOTAL** | **100** | **95** | **SUB-JUDICE** |

---

## 5. Hipóteses Refutáveis
- **H1:** A pesquisa Discovery-100 consegue atingir 100 repositórios únicos, reais e canônicos no ecossistema global sem inventar entradas e com 100% de URLs verificáveis.
- **H2:** O monitor comportamental eBPF (`behavioral_ebpf_monitor.py`) intercepta e classifica sequências anômalas de syscalls em $< 1.0\text{ ms}$ sem criar gargalos no loop de execução.
- **H3:** O gerador de entradas Rekor no `ProvenanceAttestor` produz artefatos HashedRekord conformes com a especificação Sigstore Rekor v0.0.1 em memória volátil.
- **H4:** O Z3 SMT prova matematicamente (`unsat` para contraexemplos) o Teorema 8 de Reversibilidade Monotônica de Checkpoints de Memória.
- **H5:** A suíte de 27 testes mestras atinge 100% de sucesso contínuo ao longo de 3 rodadas consecutivas (81 execuções totais).

---
*Assinado pelo Orquestrador Alpha-C7,*  
**AetherMind Engineering Cortex**
