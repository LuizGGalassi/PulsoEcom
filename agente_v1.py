import google.generativeai as genai
import feedparser
import os
import random # <-- NOVO: Para escolher fontes aleatórias
from typing import Tuple, Union
from datetime import datetime

# --- CONFIGURAÇÃO (API KEY) ---
API_KEY = os.environ.get("GOOGLE_API_KEY")

# --- MUDANÇA (CORREÇÃO DE BUG CRÍTICO) ---
# Se a chave não for encontrada, o script deve parar.
if not API_KEY:
    print("Erro Crítico: A API Key 'GOOGLE_API_KEY' não foi encontrada.")
    exit(1) # Sai do script com um código de erro

genai.configure(api_key=API_KEY)


# --- MUDANÇA (MELHORIA DE CRESCIMENTO) ---
# Damos ao agente múltiplas fontes para gerar variedade.
FONTES_RSS = {
    "r/shopify": "https://www.reddit.com/r/shopify/.rss",
    "r/shopee": "https://www.reddit.com/r/shopee/.rss",
    "e-commerce-times": "https://www.ecommercetimes.com/feed/"
}
# Arquivo de log para evitar posts duplicados
LOG_POSTS_PROCESSADOS = "_data/posts_processados.log"


# --- MÓDULO 1: O MONITOR (Atualizado) ---

def buscar_post_aleatorio() -> Tuple[Union[str, None], Union[str, None], Union[str, None]]:
    """
    Busca um post novo de uma fonte aleatória que ainda não foi processado.
    Retorna (titulo, resumo, link_id) ou (None, None, None).
    """
    
    # Carrega o log de posts já processados
    os.makedirs(os.path.dirname(LOG_POSTS_PROCESSADOS), exist_ok=True)
    if not os.path.exists(LOG_POSTS_PROCESSADOS):
        open(LOG_POSTS_PROCESSADOS, 'w').close()
        
    with open(LOG_POSTS_PROCESSADOS, 'r', encoding='utf-8') as f:
        posts_ja_processados = f.read().splitlines()

    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    
    # Pega uma fonte aleatória da nossa lista
    nome_fonte, url_fonte = random.choice(list(FONTES_RSS.items()))
    print(f"Buscando dados da fonte aleatória: {nome_fonte} ({url_fonte})")
    
    try:
        feed = feedparser.parse(url_fonte, agent=USER_AGENT)
        
        if feed.bozo:
            print(f"Erro de parsing no feed: {feed.bozo_exception}")
            return None, None, None
        
        if not feed.entries:
            print("Erro: Feed lido, mas não contém posts.")
            return None, None, None
            
        # --- LÓGICA ANTI-DUPLICATA ---
        # Em vez de pegar só o [0], procuramos o primeiro post NOVO
        for post in feed.entries:
            # 'id' ou 'link' são os melhores identificadores únicos
            link_id = post.get('id', post.get('link', ''))
            
            if not link_id:
                continue # Pula post se não tiver ID/link

            if link_id not in posts_ja_processados:
                # ENCONTRAMOS UM POST NOVO!
                print(f"Post novo encontrado: {post.title[:50]}...")
                titulo = post.title
                resumo = post.get('summary', post.get('description', ''))
                
                return titulo, resumo, link_id # Retorna o ID para o log
            
        # Se o loop terminar, todos os posts do feed já foram processados
        print("Nenhum post novo encontrado nesta fonte. Todos já estão no log.")
        return None, None, None

    except Exception as e:
        print(f"Erro inesperado ao buscar dados do RSS: {e}")
        return None, None, None

# --- MÓDULO 2: O CÉREBRO (Processamento IA) ---
# (Sem mudanças. Esta função está perfeita.)
def gerar_insight_acionavel(titulo_artigo: str, resumo_artigo: str) -> str:
    """
    Usa a IA para transformar dados brutos em um insight acionável.
    """
    prompt_template = f"""
    Objetivo: Atue como um especialista em e-commerce focado em Shopify e Shopee.
    Sua tarefa é ler o material de origem e gerar um "insight acionável" para 
    donos de pequenos negócios.

    Regras de Saída:
    1.  Crie um título curto e magnético (máx. 10 palavras).
    2.  Escreva um insight de 2 a 3 frases (máx. 50 palavras).
    3.  A linguagem deve ser direta, clara e focada na ação.

    Material de Origem:
    - Título: "{titulo_artigo}"
    - Resumo: "{resumo_artigo}"

    Insight Gerado:
    """
    try:
        model = genai.GenerativeModel('models/gemini-2.5-flash') 
        response = model.generate_content(prompt_template)
        insight_limpo = response.text.strip()
        return insight_limpo
    except Exception as e:
        print(f"Erro ao chamar a API de IA: {e}")
        return None

# --- MÓDULO 3: O PUBLICADOR (Atualizado) ---

# --- MÓDULO 3: O PUBLICADOR (Salva o Post) ---

def salvar_post_jekyll(insight_completo: str):
    """
    Pega o insight gerado pela IA, formata-o como um post
    Jekyll e o salva como um arquivo .md.
    """
    print("Iniciando Módulo 3: Publicador Estático...")

    try:
        # 1. Separar o Título do Corpo
        partes = insight_completo.split('\n\n', 1)
        if len(partes) < 2:
            print("Erro: Insight da IA não está no formato Título/Corpo esperado.")
            return

        titulo_raw = partes[0]
        corpo = partes[1].strip()

        # Limpa o título (remove os ** do Markdown)
        titulo_limpo = titulo_raw.replace("**", "").strip()

        # 2. Preparar o Nome do Arquivo (Formato Jekyll)
        hoje_str = datetime.now().strftime('%Y-%m-%d')
        slug = titulo_limpo.lower().replace(' ', '-')
        slug = "".join(c for c in slug if c.isalnum() or c in ['-']) 

        nome_arquivo = f"{hoje_str}-{slug}.md"

        # 3. Criar o "Front Matter" do Jekyll
        # ==================================================
        # A CORREÇÃO ESTÁ AQUI:
        # Trocamos "layout: post" por "layout: default"
        # ==================================================
        conteudo_front_matter = f"""---
layout: default
title: "{titulo_limpo}"
---

"""
        conteudo_completo = conteudo_front_matter + corpo

        # 4. Salvar o Arquivo
        pasta_posts = "_posts"
        os.makedirs(pasta_posts, exist_ok=True)

        caminho_arquivo = os.path.join(pasta_posts, nome_arquivo)

        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            f.write(conteudo_completo)

        print(f"--- SUCESSO: Post salvo em '{caminho_arquivo}' ---")

    except Exception as e:
        print(f"Erro ao salvar o arquivo do post: {e}")
# --- ORQUESTRADOR PRINCIPAL (Atualizado) ---

def executar_agente():
    print("--- INICIANDO AGENTE DE INTELIGÊNCIA V2 ---")
    
    # 1. Módulo 1 executa
    titulo, resumo, link_id = buscar_post_aleatorio()
    
    if titulo and resumo and link_id:
        print(f"\nDados Brutos Coletados:\n  Título: {titulo[:50]}...")
        print(f"  Resumo: {resumo[:70]}...")
        
        # 2. Módulo 2 executa
        print("\nEnviando para o Cérebro de IA (Módulo 2)...")
        insight = gerar_insight_acionavel(titulo, resumo)
        
        if insight:
            print("\n--- INSIGHT GERADO COM SUCESSO ---")
            print(insight)
            
            # 3. Módulo 3 executa
            sucesso_ao_salvar = salvar_post_jekyll(insight)
            
            # 4. MÓDULO ANTI-DUPLICATA (Final)
            if sucesso_ao_salvar:
                # Só registra no log se o arquivo foi salvo com sucesso
                with open(LOG_POSTS_PROCESSADOS, 'a', encoding='utf-8') as f:
                    f.write(f"{link_id}\n")
                print(f"Registrado '{link_id}' no log de posts processados.")
            else:
                print("Falha ao salvar o post. Não será registrado no log.")
                
        else:
            print("\nFalha ao gerar insight com os dados reais.")
    else:
        print("Nenhum post novo para processar. Encerrando o ciclo.")
        
    print("\n--- AGENTE V2 FINALIZADO ---")

# --- Ponto de Entrada do Script ---
if __name__ == "__main__":
    executar_agente()

