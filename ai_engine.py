import aiohttp
import asyncio
import io
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN_HF = os.environ.get("HF_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN_HF}"} if TOKEN_HF else {}

TEXT_API_URL = "https://api-inference.huggingface.co/models/google/gemma-1.1-2b-it"
IMAGE_API_URL = "https://api-inference.huggingface.co/models/diffusers-internal-dev/nano-banana-modular"

# Configuração de conector para contornar problemas de DNS da Render
resolver = aiohttp.AsyncResolver(nameservers=['8.8.8.8', '8.8.4.4'])
connector = aiohttp.TCPConnector(resolver=resolver)

async def generate_reply(prompt, name):
    try:
        async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=30)) as session:
            async with session.post(TEXT_API_URL, headers=HEADERS, json={"inputs": prompt}) as session_post:
                if session_post.status == 200:
                    data = await session_post.json()
                    texto_gerado = data[0].get('generated_text', '').strip() if isinstance(data, list) else data.get('generated_text', '').strip()
                    if texto_gerado.startswith(prompt): texto_gerado = texto_gerado[len(prompt):].strip()
                    return texto_gerado if texto_gerado else "pode crer mano kkk"
                return f"Erro na API: Status {session_post.status}"
    except Exception as e:
        return f"Erro de Conexão: {type(e).__name__}"

async def generate_image(prompt):
    try:
        async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=45)) as session:
            async with session.post(IMAGE_API_URL, headers=HEADERS, json={"inputs": prompt}) as session_post:
                if session_post.status == 200:
                    return io.BytesIO(await session_post.read())
                return f"Erro na API de imagem: Status {session_post.status}"
    except Exception as e:
        return f"Erro de Conexão na Imagem: {type(e).__name__}"
