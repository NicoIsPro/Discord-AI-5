import os
import discord
from discord.ext import commands
import asyncio
from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv

import ai_engine
import memory_store

# Carrega as variáveis de ambiente
load_dotenv()
TOKEN = os.environ.get("DISCORD_TOKEN")
PORT = int(os.environ.get("PORT", 10000))

memory = memory_store.MemoryStore()
intents = discord.Intents.default()
intents.message_content = True

# CONFIGURAÇÃO: O prefixo do bot agora é a própria menção (@Bot)
bot = commands.Bot(command_prefix=commands.when_mentioned, intents=intents)
app = FastAPI()

# Rota principal ajustada para aceitar GET e HEAD (evita o erro 405 na Render)
@app.api_route("/", methods=["GET", "HEAD"])
def read_root():
    return {"status": "Bot Online!", "sistema": "Ativo"}

@bot.event
async def on_ready():
    print(f"🔥 [SISTEMA] Bot logado com sucesso como {bot.user}!")
    print(f"📡 [SISTEMA] Pronto para responder menções com @{bot.user.name}")

@bot.event
async def on_message(message):
    # Ignora mensagens vindas do próprio bot
    if message.author == bot.user:
        return

    # FOCO DO BOT: Verifica se o bot foi marcado/mencionado na mensagem
    if bot.user in message.mentions:
        # Limpa o texto tirando a marcação <@ID> para enviar só a pergunta pura para a IA
        clean_content = message.content.replace(f'<@{bot.user.id}>', '').replace(f'<@!{bot.user.id}>', '').strip()
        
        # Se o usuário marcou o bot mas não digitou nada, assume um "oi"
        if not clean_content:
            clean_content = "oi"
            
        prompt = memory.get_formatted_prompt(message.author.id, clean_content, message.author.display_name)
        
        # Ativa o "Digitando..." no Discord para segurar a conexão ativa
        async with message.channel.typing():
            try:
                # Print no Log de Execução da Render para você ver a mensagem chegando ao vivo
                print(f"📩 [MENSAGEM] @Menção recebida de {message.author.display_name}: {clean_content}")
                
                reply = await ai_engine.generate_reply(prompt, message.author.display_name)
                if reply:
                    await message.reply(reply)
                else:
                    await message.reply("pode crer mano kkk")
            except Exception as e:
                print(f"[ERRO NO PROCESSAMENTO]: {e}")
                await message.reply("foi mal mano, deu um estalo aqui na mente kkk")

    # Garante o processamento interno do fluxo do discord.py
    await bot.process_commands(message)

# Inicialização paralela do Servidor Web e do Bot
async def main():
    config = uvicorn.Config(app, host="0.0.0.0", port=PORT, log_level="warning")
    server = uvicorn.Server(config)
    
    await asyncio.gather(
        server.serve(),
        bot.start(TOKEN)
    )

if __name__ == "__main__":
    if not TOKEN:
        print("[ERRO CRÍTICO] DISCORD_TOKEN não configurado!")
    else:
        print("[SISTEMA] Iniciando Servidor e Bot... Chamada por @Menção configurada.")
        asyncio.run(main())
