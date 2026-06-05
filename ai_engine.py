import aiohttp
import asyncio
import io

# Acesso anônimo (sem token)
HEADERS = {}

# URLs das APIs do Hugging Face
TEXT_API_URL = "https://api-inference.huggingface.co/models/google/gemma-1.1-2b-it"
IMAGE_API_URL = "https://api-inference.huggingface.co/models/diffusers-internal-dev/nano-banana-modular"

async def generate_reply(prompt, name):
    # O Gemma funciona melhor se formatarmos a mensagem como um chat
    gemma_prompt = f"<start_of_turn>user\n{prompt}<end_of_turn>\n<start_of_turn>model\n"
    
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            async with session.post(TEXT_API_URL, headers=HEADERS, json={"inputs": gemma_prompt}) as response:
                
                if response.status == 200:
                    data = await response.json()
                    # A API costuma devolver o seu prompt junto com a resposta, então limpamos isso
                    texto_gerado = data[0].get('generated_text', '').replace(gemma_prompt, '').strip()
                    return texto_gerado if texto_gerado else "pode crer mano kkk"
                else:
                    erro = await response.text()
                    print(f"[ERRO GEMMA] Status: {response.status} - Resposta: {erro}")
                    if response.status == 503:
                        return "O Gemma tava dormindo. Manda de novo em 20 segundos!"
                    return "Deu erro na IA de texto."

    except asyncio.TimeoutError:
        return "Demorou muito pra responder. Tenta de novo!"
    except Exception as e:
        print(f"[ERRO NO TEXTO] {e}")
        return "A conexão com a IA caiu!"

async def generate_image(prompt):
    # Aqui não mandamos o prompt formatado pro chat, só a descrição da imagem (ex: "um gato voando")
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=45)) as session:
            # A API de imagem requer as mesmas coisas, mas o retorno não é texto/JSON, é o arquivo direto
            async with session.post(IMAGE_API_URL, headers=HEADERS, json={"inputs": prompt}) as response:
                
                if response.status == 200:
                    # Lê os bytes da imagem
                    image_bytes = await response.read()
                    # Transforma os bytes em um formato que o Discord aceita enviar como arquivo
                    return io.BytesIO(image_bytes)
                else:
                    erro = await response.text()
                    print(f"[ERRO NANO BANANA] Status: {response.status} - Resposta: {erro}")
                    if response.status == 503:
                        return "O gerador de imagens Nano Banana tá ligando, espera uns 20s e tenta de novo!"
                    return f"A IA de imagem deu erro (Status {response.status})."

    except asyncio.TimeoutError:
        return "O gerador de imagens demorou demais!"
    except Exception as e:
        print(f"[ERRO NA IMAGEM] {e}")
        return "A conexão com o gerador de imagens caiu!"
