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

# Inicialização do Bot e da Memória
memory = memory_store.MemoryStore()
intents = discord.Intents.default()
intents.message_content = True  # OBRIGATÓRIO estar ativo no Discord Developer Portal

bot = commands.Bot(command_prefix="!", intents=intents)
app = FastAPI()

# Rota para a Render não encerrar o bot por inatividade
@app.get("/")
def read_root():
    return {"status": "Bot Online!", "sistema": "Ativo"}

@bot.event
async def on_ready():
    print(f"🔥 [SISTEMA] Bot logado com sucesso como {bot.user}!")
    print("[SISTEMA] Modo de escuta: Menções (@bot) e Mensagens Diretas (DM).")

# ====================================================
# EVENTO DE MENSAGENS (Focado em Menção e DM)
# ====================================================
@bot.event
async def on_message(message):
    # Ignora mensagens do próprio bot para evitar loops infinitos
    if message.author == bot.user:
        return

    # O bot só vai responder se:
    # 1. Alguém marcar ele no servidor (@NomeDoBot)
    # 2. Alguém mandar mensagem direto no privado (DM) do bot
    if bot.user in message.mentions or isinstance(message.channel, discord.DMChannel):
        
        # Remove a marcação <@id_do_bot> do texto para a IA não ler a própria menção
        clean_content = message.content.replace(f'<@{bot.user.id}>', '').strip()
        
        # Se a pessoa só marcou o bot sem digitar nada, assume um "oi"
        if not clean_content:
            clean_content = "oi"
            
        # Puxa o histórico e monta o prompt formatado
        prompt_formatado = memory.get_formatted_prompt(message.author.id, clean_content, message.author.display_name)
        
        # Ativa o "Digitando..." no Discord (mostra que o bot está processando a IA)
        async with message.channel.typing():
            try:
                # Chama a função que criamos no ai_engine.py
                reply = await ai_engine.generate_reply(prompt_formatado, message.author.display_name)
                
                if reply:
                    await message.reply(reply)
                else:
                    await message.reply("pode crer mano kkk")
                    
            except Exception as e:
                print(f"[ERRO NO PROCESSAMENTO]: {e}")
                await message.reply("foi mal mano, deu um estalo aqui na mente kkk")

    # Garante que outros comandos normais baseados em texto (ex: !ajuda) continuem funcionando
    await bot.process_commands(message)

# ====================================================
# INICIALIZAÇÃO PARALELA (FastAPI + Discord.py)
# ====================================================
async def main():
    config = uvicorn.Config(app, host="0.0.0.0", port=PORT, log_level="info")
    server = uvicorn.Server(config)
    
    # Roda a FastAPI e o Bot juntos no mesmo loop de eventos
    await asyncio.gather(
        server.serve(),
        bot.start(TOKEN)
    )

if __name__ == "__main__":
    if not TOKEN:
        print("[ERRO CRÍTICO] DISCORD_TOKEN não encontrado no ambiente!")
    else:
        print("[SISTEMA] Iniciando Servidor Web e Bot...")
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("[SISTEMA] Aplicação encerrada manualmente.")
