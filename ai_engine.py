import asyncio

async def generate_reply(prompt, name):
    # Simula a IA "pensando" por 4 segundos
    await asyncio.sleep(4)
    return f"E aí {name}! Isso é um teste. Você disse: {prompt}"
