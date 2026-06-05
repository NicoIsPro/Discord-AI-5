import aiohttp
import asyncio

API_URL = "https://api-inference.huggingface.co/models/gpt2"

async def generate_reply(prompt, name):
    # Diminuímos o tempo limite (timeout) para 5 segundos
    # Se a IA não responder em 5s, o bot para de esperar e manda uma mensagem padrão
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            async with session.post(API_URL, json={"inputs": prompt}) as response:
                if response.status == 200:
                    data = await response.json()
                    return data[0].get('generated_text', '...').strip()
                return "Tô processando, mas a IA tá demorando..."
    except Exception:
        return "A conexão com a IA caiu, tenta de novo!"
