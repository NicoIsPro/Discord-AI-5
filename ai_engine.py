import aiohttp

# Usando um modelo muito mais rápido e moderno do Google
API_URL = "https://api-inference.huggingface.co/models/google/gemma-2-2b-it"

async def generate_reply(prompt, name):
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 50, "return_full_text": False}
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    # O formato do Gemma é diferente
                    if isinstance(data, list) and len(data) > 0:
                        return data[0].get('generated_text', '...').strip()
                return "Tô processando rapidão!"
    except Exception as e:
        print(f"Erro: {e}")
        return "Tô meio lento, tenta de novo?"
