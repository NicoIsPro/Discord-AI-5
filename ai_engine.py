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

async def generate_reply(prompt, name):
    try:
        # Usamos uma sessão padrão, sem o resolver customizado
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=40)) as session:
            async with session.post(TEXT_API_URL, headers=HEADERS, json={"inputs": prompt}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    texto = data[0].get('generated_text', '').strip() if isinstance(data, list) else data.get('generated_text', '').strip()
                    if texto.startswith(prompt): texto = texto[len(prompt):].strip()
                    return texto if texto else "pode crer mano kkk"
                else:
                    return f"Erro na API: Status {resp.status}"
    except Exception as e:
        return f"Erro: {type(e).__name__}"

async def generate_image(prompt):
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
            async with session.post(IMAGE_API_URL, headers=HEADERS, json={"inputs": prompt}) as resp:
                if resp.status == 200:
                    return io.BytesIO(await resp.read())
                return f"Erro na imagem: Status {resp.status}"
    except Exception as e:
        return f"Erro de imagem: {type(e).__name__}"
