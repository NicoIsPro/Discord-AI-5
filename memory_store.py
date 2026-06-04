class MemoryStore:
    def __init__(self):
        self.history = {}

    def get_formatted_prompt(self, user_id, user_message, display_name):
        # O formato exato que o seu ai_engine.py espera para conseguir extrair o texto
        prompt = f"Apelido visível: {display_name}\nMensagem: {user_message}"
        return prompt