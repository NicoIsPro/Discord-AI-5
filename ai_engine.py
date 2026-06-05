import aiohttp
import asyncio
import os
from dotenv import load_dotenv

# Carrega o token do arquivo .env
load_dotenv()
HF_TOKEN = os.environ.get("HF_TOKEN")

API_URL = "https://api-inference.huggingface.co/models/gpt2"

async def generate_reply(prompt, name):
    # Cabeçalho de autenticação (MUITO importante para a API do Hugging Face não te bloquear)
    headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}

    # Aumentamos o timeout para 30 segundos. 
    # Motivo: Se o modelo estiver "dormindo", a primeira requisição pode demorar uns 20s.
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            async with session.post(API_URL, headers=headers, json={"inputs": prompt}) as response:
                
                # Se deu tudo certo
                if response.status == 200:
                    data = await response.json()
                    # O GPT-2 costuma retornar o texto junto com o prompt, mas isso evita o erro do JSON
                    return data[0].get('generated_text', '...').strip()
                
                # Se a API reclamar (Modelo carregando, Sem Token, etc)
                else:
                    erro = await response.text()
                    print(f"[ERRO API HF] Status: {response.status} - Resposta: {erro}")
                    
                    if response.status == 503:
                        return "O meu cérebro tava dormindo, tô acordando ele. Manda a mensagem de novo em 20 segundos!"
                    
                    return f"Deu erro na API (Status {response.status}). Olha o console!"

    except asyncio.TimeoutError:
        return "Demorou demais pra responder (mais de 30s). Tenta de novo, mano!"
    except Exception as e:
        print(f"[ERRO EXCEPTION] Falha na conexão com a IA: {e}")
        return "A conexão com a IA caiu feio!"
