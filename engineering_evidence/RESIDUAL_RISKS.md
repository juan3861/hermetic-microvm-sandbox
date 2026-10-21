# RESIDUAL RISKS: DECLARAÇÃO DE LIMITAÇÕES E FRONTEIRAS

**Data:** 2026-10-21T16:07:00-03:00  
**Classificação:** Risco Baixo / Monitorado

---

## 1. Riscos Residuais Mapeados e Mitigações

1. **Dependência de Recursos do Host para GPU DirectML**:
   - *Risco*: Em ambientes Linux puros sem `/dev/dxg` ou sem drivers proprietários da NVIDIA/AMD instalados, a aceleração de hardware faz fallback para o backend `cpu_tensor`.
   - *Mitigação*: O motor detecta automaticamente a ausência do dispositivo de hardware e reconfigura o pipeline para CPU sem lançar exceções não tratadas.
2. **Quotas de Memória RAM Volátil no WSL2 (`/dev/shm`)**:
   - *Risco*: Criar dezenas de sessões simultâneas de microVM com arquivos gigantes sem fechá-las pode saturar a partição de 7.8GB de DDR RAM tmpfs.
   - *Mitigação*: O context manager `with Sandbox() as sb:` evapora automaticamente todo o diretório na saída (`__exit__`), e o método `terminate_session` executa limpeza recursiva forçada.
3. **Restrições de Rede Privada em Swarms P2P**:
   - *Risco*: Em redes corporativas com firewalls restritivos e NAT simétrico, a descoberta de pares da malha AetherMesh pode exigir servidores de relay STUN/TURN ou túneis WireGuard.
   - *Mitigação*: A malha opera com conexões locais diretas (loopback) e túneis autenticados sobre TCP/WebSockets padrão.
