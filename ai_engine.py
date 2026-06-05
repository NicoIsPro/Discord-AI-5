import aiohttp
import asyncio
import io
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente (para puxar o HF_TOKEN do .env ou da Render)
load_dotenv()
TOKEN_HF = os.environ.get("HF_TOKEN")

# Configura o cabeçalho de autenticação (Isso tira seu bot da "lista negra" de IPs)
HEADERS = {"Authorization": f"Bearer {TOKEN_HF}"} if TOKEN_HF else {}

# URLs das APIs do Hugging Face
TEXT_API_URL = "https://api-inference.huggingface.co/models/google/gemma-1.1-2b-it"
IMAGE_API_URL = "https://api-inference.huggingface.co/models/diffusers-internal-dev/nano-banana-modular"

async def generate_reply(prompt, name):
    # Simplificamos o prompt para evitar que a API rejeite o formato
    try:
        # Timeout de 30 segundos para dar tempo de a IA processar
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            async with session.post(TEXT_API_URL, headers=HEADERS, json={"inputs": prompt}) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Trata se a API devolver uma lista (padrão) ou um dicionário puro (acontece no Gemma)
                    if isinstance(data, list) and len(data) > 0:
                        texto_gerado = data[0].get('generated_text', '').strip()
                    elif isinstance(data, dict):
                        texto_gerado = data.get('generated_text', '').strip()
                    else:
                        texto_gerado = str(data)

                    # Remove o prompt do texto se a IA repetir ele na resposta
                    if texto_gerado.startswith(prompt):
                        texto_gerado = texto_gerado[len(prompt):].strip()

                    return texto_gerado if texto_gerado else "pode crer mano kkk"
                
                else:
                    erro = await response.text()
                    print(f"[ERRO GEMMA] Status: {response.status} - Resposta: {erro}")
                    
                    if response.status == 503:
                        return "O Gemma tá iniciando o servidor deles lá. Tenta de novo em 20 segundos!"
                    if response.status == 401:
                        return "Opa, erro de autorização. O token (HF_TOKEN) não foi lido ou tá errado!"
                        
                    return f"Erro na API do Hugging Face: Status {response.status}"

    except asyncio.TimeoutError:
        return "Demorou muito pra responder. Tenta de novo, mano!"
    except Exception as e:
        print(f"[ERRO NO TEXTO] {e}")
        # AGORA VAI MOSTRAR O ERRO REAL NA TELA DO DISCORD SE CAIR!
        return f"A conexão com a IA caiu! Erro interno: {type(e).__name__} - {str(e)}"

async def generate_image(prompt):
    try:
        # Tempo um pouco maior para gerar imagens (45s) porque é mais pesado
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=45)) as session:
            async with session.post(IMAGE_API_URL, headers=HEADERS, json={"inputs": prompt}) as response:
                
                if response.status == 200:
                    image_bytes = await response.read()
                    # Retorna os bytes prontos para o Discord enviar como arquivo de imagem
                    return io.BytesIO(image_bytes)
                else:
                    erro = await response.text()
                    print(f"[ERRO NANO BANANA] Status: {response.status} - Resposta: {erro}")
                    
                    if response.status == 503:
                        return "O gerador de imagens tá ligando, espera uns 20s e tenta de novo!"
                        
                    return f"A IA de imagem deu erro (Status {response.status})."

    except asyncio.TimeoutError:
        return "O gerador de imagens demorou demais!"
    except Exception as e:
        print(f"[ERRO NA IMAGEM] {e}")
        return f"A conexão com o gerador de imagens caiu! Erro interno: {type(e).__name__} - {str(e)}"
