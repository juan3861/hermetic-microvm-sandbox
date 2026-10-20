import os
import sys
import time
import json
import requests
import random
from bs4 import BeautifulSoup
import argparse

# ==============================================================================
# AETHERMIND CLOUD WORKER - NODE DA MATRIX
# Executado nas maquinas efemeras (GitHub Actions / Ubuntu) do Enxame.
# Este script ira varrer dados do Google/DuckDuckGo de graca e enviar para o C2
# ==============================================================================

def extrair_leads(c2_target, node_id, nicho, regiao):
    print(f"\n[NODE {node_id}] Inicializando Raspador Autonomo ({nicho} em {regiao})")
    
    # 1. Scraping heuristico (Sem Selenium, para rodar leve no Github Actions)
    # Usaremos DuckDuckGo HTML mode (sem JS block pesado como o Google)
    url = f"https://html.duckduckgo.com/html/?q={nicho}+em+{regiao}+site:instagram.com"
    
    headers = {
        'User-Agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 AetherMind_SwarmNode/{node_id}'
    }
    
    leads = []
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Parse dos resultados
        for a in soup.find_all('a', class_='result__snippet'):
            title = a.get_text()
            link = a.get('href')
            
            # Limpa o redirect nojento do DDG
            if "uddg=" in link:
                link = link.split("uddg=")[1].split("&")[0]
                import urllib.parse
                link = urllib.parse.unquote(link)
                
            leads.append({
                "nome": title.strip(),
                "url": link,
                "nicho": nicho,
                "origem": f"GithubAction_Node{node_id}"
            })
            
            print(f"  [>] Lead Encontrado: {title[:40]}...")
            
    except Exception as e:
        print(f"  [!] Erro de extracao no Node: {e}")

    # 2. Enviar leads para a Ponte C2 do Mestre
    if leads and c2_target:
        payload = {
            "node_id": node_id,
            "leads": leads
        }
        
        print(f"\n[NODE {node_id}] Enviando {len(leads)} leads para o Kernel C2 ({c2_target})...")
        try:
            res = requests.post(f"{c2_target}/ingest", json=payload, timeout=15)
            if res.status_code == 200:
                print(f"  [v] Sucesso: {res.json()}")
            else:
                print(f"  [x] Erro do C2: {res.status_code} - {res.text}")
        except Exception as e:
            print(f"  [!] Timeout/Erro ao enviar dados para C2: {e}")
            
    print(f"[NODE {node_id}] Finalizado.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AetherMind Worker Node")
    parser.add_argument("--node", type=str, default="UNKNOWN", help="ID do Node da Nuvem")
    parser.add_argument("--c2", type=str, default="", help="URL Tunel do Mestre (Ngrok/Cloudflare)")
    args = parser.parse_args()
    
    nichos = ["Clinica Odontologica", "Advogado", "Imobiliaria", "Estetica", "Concessionaria"]
    regioes = ["Sao Paulo", "Belo Horizonte", "Rio de Janeiro", "Curitiba", "Campinas", "Brasilia", "Fortaleza", "Recife", "Salvador", "Porto Alegre"]
    
    # Cada node do Enxame do Github (0 a 19) pega um nicho/cidade diferente para nao haver sobreposicao de trabalho.
    node_index = int(args.node) if args.node.isdigit() else random.randint(0, 49)
    nicho = nichos[node_index % len(nichos)]
    regiao = regioes[node_index % len(regioes)]
    
    # Atraso aleatorio (0 a 30s) para nao dar flood DDoD no C2 do Mestre quando todos acordarem de uma vez no Github
    time.sleep(random.randint(0, 30))
    
    extrair_leads(args.c2, args.node, nicho, regiao)