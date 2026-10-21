# COMPONENT REUSE MANIFEST: SELEÇÃO E ADAPTAÇÃO MODULAR

## 1. Componentes Aprovados para Integração

| Componente | Repositório / Fonte de Inspiração | Licença | Estratégia de Encaixe | Módulo Destino |
|---|---|---|---|---|
| **OCI Layer Unpacker & Whiteout Merger** | `opencontainers/umoci` & OCI Image Spec v1.1 | Apache-2.0 | **Adapter/Bridge Pattern** (Python Standard `tarfile` + `hashlib` em `/dev/shm`) | `mcp/oci_image_unpacker.py` |
| **MicroVM Fault-Tolerant Watchdog** | `vhive-serverless/vHive` & Firecracker Snapshots | Apache-2.0 | **Native API Integration** (Hook no `MicroVMSessionManager` com captura de sinais) | `core/fault_tolerant_watchdog.py` |
| **Adversarial Syscall & Stress Fuzzer** | `google/syzkaller` & Linux seccomp-tests | Apache-2.0 | **Plug-and-play Verification Module** (Testa `GVisorSentryGuard` e `SiliconBridge`) | `security/adversarial_syscall_fuzzer.py` |

---

## 2. Critérios de Aceitação por Componente

1. **`mcp/oci_image_unpacker.py`**:
   - Criação de bundle OCI válido com `config.json` e `rootfs/`.
   - Extração de camadas tar.gz com resolução correta de hashes SHA-256 de blobs.
   - Tratamento de whiteouts (`.wh.<file>`) para remoção de arquivos criados em camadas inferiores.
   - Extração 100% contida em DDR RAM (`/dev/shm`) sem permissão de root.
2. **`core/fault_tolerant_watchdog.py`**:
   - Detecção em tempo real de crash de processo (`returncode in (137, 139, 124)`).
   - Acionamento automático de rollback para o checkpoint limpo em $< 5\text{ ms}$.
   - Retorno de telemetria com diagnóstico de causa raiz (OOM, Segfault, CPU Hang).
3. **`security/adversarial_syscall_fuzzer.py`**:
   - Execução de bateria com 100 variações de payloads adversariais e chamadas de sistema proibidas.
   - Taxa de contenção de 100% (`blocked_count == 100`).
