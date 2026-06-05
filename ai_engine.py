import os
from groq import AsyncGroq

chave_api = os.environ.get("GROQ_API_KEY")
client = AsyncGroq(api_key=chave_api)

async def generate_reply(prompt, name):
    print(f"🤖 [IA] Enviando texto para a Groq: '{prompt}'")
    
    if not chave_api:
        return "❌ Erro: Chave GROQ_API_KEY não encontrada nas variáveis da Render."

    try:
        # REMOVIDO O TIMEOUT: Dá tempo para o servidor gratuito processar sem pressa
        completion = await client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant"
        )
        
        resposta = completion.choices[0].message.content
        print("✅ [IA] Resposta recebida da Groq com sucesso!")
        return resposta

    except Exception as e:
        # Se der erro, o bot vai te dizer na cara no Discord qual foi o erro técnico!
        print(f"💥 ERRO INTERNO GROQ: {e}")
        return f"Deu ruim aqui mano! Erro técnico: {str(e)}"
