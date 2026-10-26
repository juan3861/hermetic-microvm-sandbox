# SEARCH QUERIES AND RESEARCH LIMITS (DISCOVERY-100)
**Protocol:** Alpha-C7 Discovery-100  
**Target:** 100 Unique, Canonical, Real Repositories  

---

## 1. Famílias de Consulta Sistemáticas
Para cobrir exaustivamente o nicho sem fabricação de dados, foram estruturadas 8 famílias de pesquisa:

1. **Família A (MicroVMs & Runtimes de Baixo Nível):**
   - Termos: `firecracker microvm rust`, `cloud-hypervisor kvm`, `google gvisor sentry`, `containers bubblewrap`, `landlock lsm linux`, `crun oci runtime`.
2. **Família B (WebAssembly & Capability Sandboxes):**
   - Termos: `bytecodealliance wasmtime`, `wasmer sandbox`, `runwasi containerd`, `lucet wasm native`.
3. **Família C (Agent Sandboxes & AI Code Execution):**
   - Termos: `e2b-dev E2B code interpreter`, `modal-labs modal client`, `daytonaio daytona dev environment`, `openhands agent runtime`, `swe-bench execution`.
4. **Família D (eBPF & Kernel Security Observability):**
   - Termos: `aquasecurity tracee ebpf`, `iovisor bcc bpf compiler`, `cilium ebpf go`, `parca continuous profiling`, `falco security falco`.
5. **Família E (Supply Chain, Provenance & Transparency Logs):**
   - Termos: `sigstore cosign`, `sigstore rekor transparency log`, `in-toto in-toto-golang`, `slsa-framework slsa-verifier`, `theupdateframework tuf`.
6. **Família F (Memory State Checkpointing & Tree Branching):**
   - Termos: `checkpoint-restore criu`, `userfaultfd linux memory snapshot`, `princeton-nlp tree-of-thought-llm`, `zram ram compression`.
7. **Família G (Formal Verification & SMT Solvers):**
   - Termos: `Z3Prover z3 theorem prover`, `CVC5 cvc5 smt`, `model checking smt-switch`, `kani rust formal verifier`.
8. **Família H (Network Egress & SSRF Protection):**
   - Termos: `stripe smokescreen egress proxy`, `envoyproxy envoy`, `cilium network policy`, `projectdiscovery httpx`.

---

## 2. Regras de Deduplicação e Limites
- **Deduplicação Canônica:** Forks, mirrors ou repositórios renomeados foram consolidados em sua identidade canônica de upstream.
- **Verificabilidade:** Todo repositório listado deve ter URL ativa em `https://github.com/...` ou domínio oficial de fundação open source.
- **Zero Alucinação:** Proibido inventar URLs fictícias ou pacotes inexistentes.
