import os
from groq import Groq

# Coloque sua chave no ambiente (na Render, adicione a variável GROQ_API_KEY)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

async def generate_reply(prompt, name):
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192", # Modelo super rápido e inteligente
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Erro na Groq: {e}")
        return "Tô dando umas falhadas na conexão, tenta dnv!"
