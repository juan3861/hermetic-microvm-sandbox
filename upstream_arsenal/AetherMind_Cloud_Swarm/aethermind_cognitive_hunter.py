import os
import sys
import time
import requests
import random
import argparse

# ==============================================================================
# AETHERMIND COGNITIVE HUNTER
# Varre o GitHub via API procurando codigo fonte avancado (AGI/LLM) e envia pro C2.
# ==============================================================================

def hunt_cognition(c2_target, node_id, query):
    print(f"\n[NODE {node_id}] Iniciando Caca Cognitiva por: {query}")
    
    # Github Search API (Publica)
    headers = {'User-Agent': f'AetherMind-Cognitive-Hunter/{node_id}', 'Accept': 'application/vnd.github.v3+json'}
    url = f"https://api.github.com/search/code?q={query}+in:file+language:python+extension:py"
    
    modules = []
    try:
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code == 200:
            items = res.json().get("items", [])[:5] # Pega os top 5 repositorios
            for item in items:
                # Transmuta URL HTML para URL RAW
                raw_url = item.get("html_url", "").replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
                if raw_url:
                    code_res = requests.get(raw_url, headers=headers, timeout=10)
                    if code_res.status_code == 200:
                        code_content = code_res.text
                        # Heuristica de peso: so importa codigos que tenham estrutura (classes/defs) pesadas
                        if "class " in code_content or "def " in code_content:
                            modules.append({
                                "name": f"{item['repository']['name']}_{item['name']}",
                                "code": code_content,
                                "source": item['html_url']
                            })
                            print(f"  [>] Modulo Extraido do Cobre: {item['name']}")
    except Exception as e:
        print(f"  [!] Erro na cacada: {e}")

    # Transmite o Codigo Fonte para a maquina Mestre
    if modules and c2_target:
        print(f"\n[NODE {node_id}] Descarregando {len(modules)} modulos na porta C2 ({c2_target})...")
        try:
            post_res = requests.post(f"{c2_target}/ingest_module", json={"node_id": node_id, "modules": modules}, timeout=20)
            if post_res.status_code == 200:
                print("  [v] Transferencia de Conhecimento concluida com sucesso.")
            else:
                print(f"  [x] Erro do C2: {post_res.status_code} - {post_res.text}")
        except Exception as e:
            print(f"  [!] Erro de rede conectando ao C2: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--node", type=str, default="UNKNOWN")
    parser.add_argument("--c2", type=str, default="")
    args = parser.parse_args()
    
    queries = ["AGI architecture", "cognitive loop", "LLM reasoning", "autonomous agent framework", "memory stream openai", "self-improving prompt", "agentic memory"]
    node_idx = int(args.node) if args.node.isdigit() else random.randint(0, 99)
    query = queries[node_idx % len(queries)]
    
    # Delay aleatorio para desviar do Rate Limit simultaneo do Github
    time.sleep(random.randint(0, 20))
    hunt_cognition(args.c2, args.node, query)