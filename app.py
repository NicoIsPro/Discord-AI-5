import os
import discord
from discord.ext import commands
import ai_engine  # Puxa o seu arquivo de IA com as gírias atualizadas

# Configuração dos Intents (permissões obrigatórias do Discord)
intents = discord.Intents.default()
intents.message_content = True  # Permite que o bot leia o texto das mensagens

# Inicializa o bot (o prefixo tanto faz porque ele responde por menção)
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Miguel está vivíssimo e logado como {bot.user.name}!")

@bot.event
async def on_message(message):
    # Regra 1: Ignora as mensagens do próprio bot para evitar loops infinitos
    if message.author == bot.user:
        return

    # Regra 2: Só responde se o bot for marcado (@Miguel)
    if bot.user.mentioned_in(message):
        try:
            # Captura o contexto e mostra o status "Digitando..." no Discord
            ctx = await bot.get_context(message)
            async with ctx.typing():
                
                # Remove a marcação do bot para enviar apenas a pergunta real para a Groq
                prompt = message.content.replace(f'<@{bot.user.id}>', '').strip()
                
                # Proteção caso o usuário envie apenas a menção vazia ou só um "?"
                if not prompt or prompt == "?":
                    prompt = "fala tu"

                # Envia o texto para o ai_engine.py e espera a resposta da IA
                resposta = await ai_engine.generate_reply(prompt, message.author.name)
                
                # Responde o usuário marcando ele de volta
                await message.reply(resposta)

        except Exception as e:
            # 🛡️ ARMADURA ANTI-CRASH: Se a Groq travar ou bloquear por spam,
            # o erro é printado no console da Render, o bot avisa no chat,
            # mas o script CONTINUA RODANDO sem cair!
            print(f"💥 [Erro Protegido] Falha ao processar mensagem: {e}")
            await message.reply("oxi cara? deu um erro interno aqui, tenta dnv dps kkk")

# Puxa o token secreto do seu bot das configurações da Render
token = os.environ.get("DISCORD_TOKEN")
if token:
    bot.run(token)
else:
    print("❌ Erro Crítico: A variável DISCORD_TOKEN não foi configurada na Render.")
