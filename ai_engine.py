import aiohttp

# Usando o GPT-2 porque é minúsculo e responde na hora
API_URL = "https://api-inference.huggingface.co/models/gpt2"

async def generate_reply(prompt, name):
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 30}}
    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                return data[0].get('generated_text', '...').strip()
            return "Tô processando!"
