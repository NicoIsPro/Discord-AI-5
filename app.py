import os
import discord
from discord.ext import commands
import asyncio
from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv

import ai_engine
import memory_store

load_dotenv()
TOKEN = os.environ.get("DISCORD_TOKEN")
# A Render exige que a aplicação use a porta que ela mandar (padrão 10000)
PORT = int(os.environ.get("PORT", 10000))

memory = memory_store.MemoryStore()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!", 
    intents=intents,
    heartbeat_timeout=60.0
)

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Bot Online na Render!", "sistema": "Ativo"}

@bot.event
async def on_ready():
    print(f"🔥 [SISTEMA] Bot logado com sucesso como {bot.user}!")
    print(f"[SISTEMA] Inicializando o servidor Web na porta {PORT}...")
    
    config = uvicorn.Config(app, host="0.0.0.0", port=PORT, log_level="info")
    server = uvicorn.Server(config)
    asyncio.create_task(server.serve())

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user in message.mentions or isinstance(message.channel, discord.DMChannel):
        clean_content = message.content.replace(f'<@{bot.user.id}>', '').strip()
        
        if not clean_content:
            clean_content = "oi"
            
        prompt = memory.get_formatted_prompt(message.author.id, clean_content, message.author.display_name)
        
        async with message.channel.typing():
            try:
                reply = await ai_engine.generate_reply(prompt, message.author.display_name)
                
                if reply:
                    await message.reply(reply)
                else:
                    await message.reply("pode crer mano kkk")
                    
            except Exception as e:
                print(f"[ERRO NO PROCESSAMENTO]: {e}")
                await message.reply("foi mal mano, deu um estalo aqui na minha mente kkk")

if __name__ == "__main__":
    if not TOKEN:
        print("[ERRO CRÍTICO] DISCORD_TOKEN não configurado!")
    else:
        print("[SISTEMA] Forçando conexão direta com o Discord...")
        bot.run(TOKEN)