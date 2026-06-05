import os
import discord
from discord.ext import commands
import asyncio
from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv

import ai_engine
import memory_store

# Carrega variáveis de ambiente
load_dotenv()
TOKEN = os.environ.get("DISCORD_TOKEN")
PORT = int(os.environ.get("PORT", 10000))

# Inicialização
memory = memory_store.MemoryStore()
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
app = FastAPI()

# Rota para a Render não encerrar o bot por inatividade
@app.get("/")
def read_root():
    return {"status": "Bot Online!", "sistema": "Ativo"}

@bot.event
async def on_ready():
    print(f"🔥 [SISTEMA] Bot logado com sucesso como {bot.user}!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user in message.mentions or isinstance(message.channel, discord.DMChannel):
        clean_content = message.content.replace(f'<@{bot.user.id}>', '').strip()
        if not clean_content:
            clean_content = "oi"
            
        prompt = memory.get_formatted_prompt(message.author.id, clean_content, message.author.display_name)
        
        # O 'typing' mostra que o bot está processando, evitando o erro de "não respondendo"
        async with message.channel.typing():
            try:
                reply = await ai_engine.generate_reply(prompt, message.author.display_name)
                if reply:
                    await message.reply(reply)
                else:
                    await message.reply("pode crer mano kkk")
            except Exception as e:
                print(f"[ERRO NO PROCESSAMENTO]: {e}")
                await message.reply("foi mal mano, deu um estalo aqui na mente kkk")

# Estrutura assíncrona para rodar servidor Web e Bot em paralelo
async def main():
    config = uvicorn.Config(app, host="0.0.0.0", port=PORT)
    server = uvicorn.Server(config)
    
    # Executa o servidor Web e o bot simultaneamente
    await asyncio.gather(
        server.serve(),
        bot.start(TOKEN)
    )

if __name__ == "__main__":
    if not TOKEN:
        print("[ERRO CRÍTICO] DISCORD_TOKEN não configurado!")
    else:
        print("[SISTEMA] Iniciando Servidor e Bot...")
        asyncio.run(main())
