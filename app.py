import os
import discord
from discord.ext import commands
import ai_engine
import asyncio
from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    token = os.environ.get("DISCORD_TOKEN")
    if token:
        asyncio.create_task(bot.start(token))
        print("🤖 [Sistema] Inicialização do Miguel agendada em segundo plano!")
    else:
        print("❌ Erro Crítico: A variável DISCORD_TOKEN não foi configurada.")
    yield
    if not bot.is_closed():
        await bot.close()

app = FastAPI(lifespan=lifespan)

@app.api_route("/", methods=["GET", "HEAD"])
def read_root():
    return {"status": "Miguel ta vivo", "sistema": "Blindado"}

@bot.event
async def on_ready():
    print(f"✅ Miguel está vivíssimo e logado como {bot.user.name}!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message):
        try:
            ctx = await bot.get_context(message)
            async with ctx.typing():
                
                prompt = message.content.replace(f'<@{bot.user.id}>', '').strip()
                
                if not prompt or prompt == "?":
                    prompt = "fala tu"

                # 🌟 AJUSTE AQUI: Mudamos de message.author.name para message.author.id
                resposta = await ai_engine.generate_reply(prompt, message.author.id)
                await message.reply(resposta)

        except Exception as e:
            print(f"💥 [Erro Protegido] Falha ao processar mensagem: {e}")
            await message.reply("oxi cara? deu um erro interno aqui, tenta dnv dps kkk")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
