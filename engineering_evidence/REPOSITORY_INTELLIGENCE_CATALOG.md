# REPOSITORY INTELLIGENCE CATALOG: ADVANCED OPEN-SOURCE ARSENAL

## 1. Mapeamento de Tecnologias Concorrentes e Candidatas

| Repositório / Referência | Domínio Tecnológico | Licença | Classificação | Vantagens Técnicas | Limitações Observadas |
|---|---|---|:---:|---|---|
| **opencontainers/umoci** | OCI Image Specification Rootless Unpacker | Apache-2.0 | **SOTA VERIFIED** | Unpack completo de camadas OCI com suporte a whiteouts (`.wh.`) e mapeamento UID/GID sem root. | Binário em Go externo; requer integração via protocolo/adaptador Python puro para zero-dependency. |
| **containers/crun** | OCI Runtime C de Baixa Latência | GPL-2.0 / LGPL-2.1 | **PRODUCTION-GRADE** | Escrito em C, extremamente rápido (~5ms), baixo consumo de memória, suporte a Landlock LSM. | Requer compilação e dependências de sistema Linux no host. |
| **e2b-dev/E2B** | Firecracker MicroVMs para Agentes | Apache-2.0 | **PRODUCTION-GRADE** | Interface padronizada para agentes LLM, pause/resume em memória. | Ausência de suporte a GPU, dependência de nuvem proprietária paga (~700ms cold start). |
| **google/gvisor** | User-space Application Kernel (Sentry/Gofer) | Apache-2.0 | **PRODUCTION-GRADE** | Interceptação de chamadas de sistema em espaço de usuário, blindagem do kernel host. | Sobrecarga de ~20-30% em syscalls pesadas, cold-start lento (~2.4s). |
| **google/syzkaller** | Coverage-Guided Syscall Fuzzer | Apache-2.0 | **SOTA VERIFIED** | Geração e mutação inteligente de argumentos de syscall para quebra de kernels. | Complexidade massiva de infraestrutura e dependência de QEMU. |
| **vhive-serverless/vHive** | MicroVM Snapshots & Live Migration | Apache-2.0 | **RESEARCH-GRADE** | Otimização de tempo de cold-start de funções serverless via snapshots em memória. | Focado em clusters Kubernetes/Knative pesados. |

---

## 2. Decisão de Seleção Tecnológica (Pareto Frontier)

Aplicando o princípio de **Compatibilidade Máxima e Baixo Atrito de Integração (Compatibility-First Engineering)**:
1. **OCI Image Layer Unpacker (`mcp/oci_image_unpacker.py`)**:
   - *Decisão*: Implementar um descompactador puro e nativo de OCI Image Layout v1.1 com suporte a tarballs comprimidos em gzip/zstd, resolução de manifests SHA-256 e tratamento de whiteouts (`.wh.*`), descompactando 100% em volatile DDR RAM (`/dev/shm`).
   - *Benefício*: Independência total do Docker daemon e de binários externos; qualquer agente pode baixar e rodar contêineres OCI na microVM.
2. **Auto-Healing MicroVM Watchdog (`core/fault_tolerant_watchdog.py`)**:
   - *Decisão*: Integrar o mecanismo de recuperação de falhas inspirado no vHive/Firecracker. Quando uma tarefa do agente falhar por SIGSEGV (139), SIGKILL/OOM (137) ou timeout (124), o watchdog executa rollback atômico para o snapshot limpo mais recente.
3. **Adversarial Syscall Fuzzer (`security/adversarial_syscall_fuzzer.py`)**:
   - *Decisão*: Construir um fuzzer adversarial inspirado no Syzkaller/Trinity que dispara 100 chamadas e mutações de syscalls restritas (ptrace, pivot_root, reboot, kexec, bpf, raw_sockets, memory_exhaustion) e audita se o gVisor Sentry e o Seccomp-BPF bloqueiam 100% delas.
