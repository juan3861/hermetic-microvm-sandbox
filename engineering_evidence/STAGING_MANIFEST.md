# STAGING MANIFEST (ALPHA-C7 DISCOVERY-100)
**Protocol:** Alpha-C7 Discovery-100  
**Staging Directory:** `external_component_candidates/selected/`  
**Counters:** `FOUND_UNIQUE=100/100, PREVIEWED=100, DEEP_REVIEWED=25, STAGED=3, INTEGRATED=3, VERIFIED=3, UNVERIFIED=0`  

---

## 1. Engrenagens Selecionadas para Staging (Relevância $\ge 80$, Prontidão $\ge 80$)

### GEAR-01: Aqua Security Tracee / IOVisor eBPF Event Model Adapter
- **Origem:** `https://github.com/aquasecurity/tracee`
- **Licença:** Apache-2.0 (Permissiva, compatível)
- **Relevância:** 96 / 100
- **Prontidão:** 92 / 100
- **Lacuna Alvo:** GAP-1 (Monitoramento Comportamental de Syscalls e Análise de Anomalias em RAM)
- **Staging Path:** `external_component_candidates/selected/tracee_ebpf_adapter.py`
- **Produção Target:** `security/behavioral_ebpf_monitor.py`
- **Gate Check:** APROVADO. Zero dependência de daemon root externo; adaptador emulado/live de anel de eventos em `/dev/shm`.

---

### GEAR-02: Sigstore Rekor HashedRekord v0.0.1 Entry Generator
- **Origem:** `https://github.com/sigstore/rekor`
- **Licença:** Apache-2.0 (Permissiva, compatível)
- **Relevância:** 97 / 100
- **Prontidão:** 92 / 100
- **Lacuna Alvo:** GAP-2 (Geração Local de Entradas Rekor para Sigstore Bundle)
- **Staging Path:** `external_component_candidates/selected/rekor_hashedrekord_generator.py`
- **Produção Target:** `security/provenance_attestor.py`
- **Gate Check:** APROVADO. Formatação Merkle Tree leaf hash e payload HashedRekord offline sem chamadas de rede externas.

---

### GEAR-03: Microsoft Z3 SMT Formal Reversibility Invariant (Teorema 8)
- **Origem:** `https://github.com/Z3Prover/z3`
- **Licença:** MIT (Permissiva, compatível)
- **Relevância:** 99 / 100
- **Prontidão:** 95 / 100
- **Lacuna Alvo:** GAP-3 (Teorema Formal de Reversibilidade Monotônica e Não-Vazamento Entrópico)
- **Staging Path:** `external_component_candidates/selected/z3_checkpoint_reversibility_theorem.py`
- **Produção Target:** `core/formal_invariants_prover.py`
- **Gate Check:** APROVADO. Formulação matemática rigorosa com verificação `unsat`.
