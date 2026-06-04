import os
import random
import re
import time
import aiohttp
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.environ.get("HF_TOKEN")
API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-1.5B-Instruct"

print("[SISTEMA] Motor configurado para usar Qwen 2.5 via API Serverless!")

ACTIVE_USERS = set()
LAST_MSG_TIME = {}

def _looks_like_call_request(prompt: str) -> bool:
    t = prompt.lower().strip()
    strong_intents = ("me liga agora", "pode me ligar", "liga pra mim", "entra na call", "vem call")
    if any(x in t for x in strong_intents): return True
    return sum(1 for w in ("call", "ligar", "chamada", "voz") if w in t) >= 2

def _extract_user_message(prompt: str) -> str:
    match = re.search(r"Mensagem:\s*(.+)", prompt, flags=re.DOTALL)
    return match.group(1).split("\n")[0].strip() if match else prompt

def _extract_display_name(prompt: str) -> str:
    match = re.search(r"Apelido visível:\s*(.+)", prompt)
    return match.group(1).strip() if match else "mano"

def _call_excuse(name: str) -> str:
    name = name.split()[0]
    return random.choice([f"boa {name}, n consigo entrar em call agr, sem fone kkk", "tá osso de ir call agr bro"])

async def _generate_with_api(user_text: str, name: str) -> str:
    system_prompt = f"Você é um jovem brasileiro descolado conversando no Discord. O usuário é o {name}. Seja natural, curto e use gírias leves (mano, papo reto, tlgd). Não fale como IA."
    
    prompt_completo = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{user_text}<|im_end|>\n<|im_start|>assistant\n"
    
    headers = {}
    if HF_TOKEN:
        headers["Authorization"] = f"Bearer {HF_TOKEN}"
        
    payload = {
        "inputs": prompt_completo,
        "parameters": {
            "max_new_tokens": 150,
            "temperature": 0.75,
            "return_full_text": False
        }
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, json=payload, headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                if isinstance(result, list) and len(result) > 0:
                    resposta = result[0].get("generated_text", "").strip()
                    resposta = resposta.replace("<|im_end|>", "").replace("<|im_start|>", "").strip()
                    return resposta if resposta else "pode crer kkk"
            
            print(f"[ERRO API] Status: {response.status}")
            return "pode crer kkk (deu um delay aqui na minha mente)"

async def generate_reply(prompt: str, display_name: str | None = None) -> str:
    if not prompt.strip(): return "manda ai pô"

    user_text = _extract_user_message(prompt)
    name = (display_name or _extract_display_name(prompt)).split()[0]
    user_key = name.lower()

    current_time = time.time()
    if user_key in LAST_MSG_TIME and (current_time - LAST_MSG_TIME[user_key] < 3):
        return f"calma ai {name}, n precisa spamar kkk"
    LAST_MSG_TIME[user_key] = current_time

    if user_key in ACTIVE_USERS:
        return "perai bro, tô terminando de ler a outra que vc mandou kkk"
    ACTIVE_USERS.add(user_key)

    try:
        if _looks_like_call_request(user_text):
            return _call_excuse(name)

        print(f"[IA] Processando {name} via Hugging Face Cloud...")
        return await _generate_with_api(user_text, name)

    except Exception as e:
        print(f"[ERRO CRÍTICO ENGINE]: {e}")
        return "buguei feio agr kkk dps vejo isso"
    finally:
        ACTIVE_USERS.remove(user_key)