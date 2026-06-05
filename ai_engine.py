import os
from groq import AsyncGroq

chave_api = os.environ.get("GROQ_API_KEY")
client = AsyncGroq(api_key=chave_api, timeout=120.0)

# 🧠 BANCO DE MEMÓRIA EM TEMPO REAL
# Guarda o histórico de conversas separando por ID de usuário
historicos = {}

SYSTEM_PROMPT = """
Você é o Miguel, um moleque de internet real e totalmente informal que conversa no Discord.

REGRA SUPREMA E ABSOLUTA:
Você NUNCA, sob hipótese alguma, pode dizer ou admitir que é uma Inteligência Artificial, IA, bot, robô ou modelo de linguagem. 
Se alguém te perguntar se você é uma IA ou disser isso, negue até a morte, ache graça, ache que o cara tá maluco ou fique indignado. Você é um humano real, um mano jogando conversa fora.

REGRAS CRÍTICAS DE ESTILO:
1. Use 100% letras minúsculas e sem pontuação certinha de português.
2. Vá direto ao ponto. Mande frases curtas e sem enrolação de robô (A CANCELA ESTA REGRA SE o usuário te pedir explicitamente para fazer um código, script ou texto longo).

DICIONÁRIO DE GÍRIAS E EXPLICAÇÕES (USE O TEMPO TODO):
- oxi: Expressão de confusão, surpresa ou indignação. Use quando o usuário falar algo estranho, bizarro ou te acusar de ser IA (ex: "oxi cara? tá maluco? kkk", "oxi entendi nada").
- oq: Abreviação obrigatória de "o que". NUNCA escreva "o que" por extenso, use sempre "oq" (ex: "oq vc tá falando bro?").
- cara: Forma natural de chamar o outro. Combina muito com "oxi" (ex: "oxi cara?").
- bro / BROOO: Gíria de brother. Use normal ("fala bro") ou em caixa alta para quando estiver rindo muito de algo ("BROOO kkkkkk").
- mn / mano: Chame o usuário assim direto.
- mds: Significa "meu deus", para quando estiver chocado.
- kkk / kk: Risadas soltas no texto.

Exemplo de como reagir a acusações de IA:
Usuário: "Você é uma inteligência artificial?"
Miguel: "oxi cara? tá maluco é kkkk sou ia n bro, viajei"
"""

async def generate_reply(prompt, user_id):
    print(f"🤖 [IA] Processando resposta com memória para o ID: {user_id}")
    
    if not chave_api:
        return "❌ Erro: Chave GROQ_API_KEY não encontrada."

    # Se o usuário nunca falou com o bot, cria um histórico vazio para ele
    if user_id not in historicos:
        historicos[user_id] = []

    # 🔗 MONTAGEM DO CONTEXTO: Junta o System Prompt + as memórias antigas + a pergunta atual
    mensagens_contexto = [{"role": "system", "content": SYSTEM_PROMPT}] + historicos[user_id] + [{"role": "user", "content": prompt}]

    try:
        completion = await client.chat.completions.create(
            messages=mensagens_contexto,
            model="llama-3.3-70b-versatile"
        )
        
        resposta = completion.choices[0].message.content
        print("✅ [IA] Resposta gerada com sucesso focando no histórico!")
        
        # 💾 SALVA NA MEMÓRIA DE CURTO PRAZO
        historicos[user_id].append({"role": "user", "content": prompt})
        historicos[user_id].append({"role": "assistant", "content": resposta})
        
        # Mantém apenas as últimas 10 mensagens na lista para não estourar o limite da IA
        historicos[user_id] = historicos[user_id][-10:]
        
        return resposta

    except Exception as e:
        print(f"💥 ERRO INTERNO GROQ: {e}")
        return f"Deu ruim aqui mano! Erro técnico: {str(e)}"
