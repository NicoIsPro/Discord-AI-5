import aiohttp
import asyncio
import io
import os
import socket
from dotenv import load_dotenv

load_dotenv()
TOKEN_HF = os.environ.get("HF_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN_HF}"} if TOKEN_HF else {}

# URLs baseadas em IP (quando possível) ou mantendo a URL, mas com timeout agressivo
TEXT_API_URL = "https://api-inference.huggingface.co/models/google/gemma-1.1-2b-it"

async def generate_reply(prompt, name):
    # Usamos o conector com 'force_close=True' para evitar que o servidor 
    # mantenha conexões "zumbis" que causam erro de DNS
    connector = aiohttp.TCPConnector(ssl=False, force_close=True)
    
    try:
        async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=20)) as session:
            async with session.post(TEXT_API_URL, headers=HEADERS, json={"inputs": prompt}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    texto = data[0].get('generated_text', '').strip() if isinstance(data, list) else data.get('generated_text', '').strip()
                    if texto.startswith(prompt): texto = texto[len(prompt):].strip()
                    return texto if texto else "pode crer mano kkk"
                else:
                    return f"Erro na API: Status {resp.status}"
    except Exception as e:
        return f"Erro de conexão (o bot perdeu o caminho): {type(e).__name__}"
