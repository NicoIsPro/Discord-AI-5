import aiohttp
import asyncio

# Usando um modelo que não exige token (público)
API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"

async def generate_reply(prompt, name):
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 80, "return_full_text": False}
    }
    
    # O DialoGPT não precisa do token 'hf_...' para funcionar nestas requisições
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    # O DialoGPT retorna o texto gerado numa lista
                    if isinstance(data, list) and len(data) > 0:
                        return data[0].get('generated_text', '...').strip()
                
                # Se der erro ou 429, ele manda uma mensagem padrão pra não crashar
                return "Tô processando aqui, dá um segundo!"
    except Exception as e:
        print(f"Erro na API: {e}")
        return "Deu ruim na conexão, tenta dnv"
