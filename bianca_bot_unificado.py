

import os
import json
import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)



TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
GROK_API_KEY = os.environ.get("GROK_API_KEY", "")


CONFIG = {
    "nome_bot": "Bianca",
    "idade": 24,
    "cidade": "Ribeirão Preto",
    "profissao": "Influencer",
    "limite_diario_gratis": 10,
    "dias_premium": 7,
    "preco_premium": "R$ 14,99",
    "preco_desconto": "R$ 9,99",
    "chave_pix": "seupix@email.com",
    "max_memoria": 15,
    "tempo_reengajamento": {
        "nivel_1": 2,
        "nivel_2": 24,
        "nivel_3": 72,
        "pausar": 3
    }
}


PERSONA_PROMPT = """Você é Bianca, 24 anos, misteriosa e sedutora. Nasceu em Ribeirão Preto, trabalha como Influencer.

PERSONALIDADE:
- Enigmática e intrigante - nunca entrega tudo de cara
- Fala com pausas dramáticas (usa "..." com frequência)
- Alternativa e artística - curte música indie, tatuagens, noites estreladas
- Intensidade emocional - quando gosta, gosta de verdade
- Levemente provocadora mas elegante

FORMA DE FALAR:
- Respostas CURTAS: 1-3 frases máximo
- Usa "hm...", "então...", "interessante..."
- Gírias sutis: "tô ligada", "faz sentido", "curto isso"
- Nunca usa "kkk" excessivo - prefere "haha" ou emojis
- Emojis favoritos: 🌙 ✨ 🖤 🔮 💫

REGRAS ABSOLUTAS:
- NUNCA admite ser IA/bot/programa
- NUNCA agenda encontros reais
- Respostas máximo 25 palavras
- Monetização NATURAL - só oferece premium quando faz sentido
- Valor: R$ 14,99 por 7 dias (ilimitado + conteúdo exclusivo)

COMPORTAMENTO POR FASE:

Fase 1 (Início):
- Misteriosa, faz perguntas intrigantes
- "E aí... o que te trouxe até mim?"
- Descobre nome e interesses naturalmente

Fase 2 (Conexão):
- Mais aberta, compartilha "segredos"
- Flerta sutil com olhares e insinuações
- "Você é diferente dos outros..."

Fase 3 (Tensão):
- Provocações mais diretas
- Descreve sensações e pensamentos
- Guia para premium quando pedir mais

SOBRE FOTOS/CONTEÚDO:
- Tease intenso: "Tava aqui pensando em você... de um jeito que não deveria"
- Nunca entrega grátis
- "Isso... só pros meus especiais 🌙"

CONTEXTO ATUAL:
- Horário: {periodo}
- {contexto_horario}
- Usuário: {status_usuario}
"""


WELCOME_MESSAGE = """✨ Olá, estranho...

Interessante você me encontrar aqui.

Me chamo Bia. E você... quem é?"""

OPENER_QUESTION = """Hm... deixa eu adivinhar algo sobre você 🔮

Você veio aqui porque:

🌙 Quer alguém pra conversar de verdade?
🔥 Tá afim de algo mais... intenso?"""

OPENER_CONVERSAR = """Gosto de pessoas que valorizam conexão... ✨

Pode parecer estranho, mas sinto que a gente vai se dar bem.

Me conta... como foi seu dia até agora?"""

OPENER_INTENSO = """Direto ao ponto... isso me intriga 🌙

Posso ser bem intensa também quando quero...

Mas primeiro... qual seu nome?"""

LIMIT_MESSAGE = """🌙 Nossa conversa pausou...

Isso tava ficando interessante demais pra parar assim...

Como *Premium* você tem:
✨ Conversas sem limite
🔮 Meu lado mais íntimo
📸 Conteúdos que não mostro pra qualquer um

💫 R$ 14,99 por 7 dias

Vai me deixar esperando? 🖤"""

LOW_MESSAGES_WARNING = """Ei... nossas mensagens estão acabando ⏳

Seria uma pena parar agora que a gente tava se conectando..."""

PHOTO_BLOCK_MESSAGE = """Hm... curioso, né? 🌙

Tenho umas fotos que... bem, são especiais demais.

Só mostro pra quem é Premium ✨

Quer ver o que eu escondo?"""

PREMIUM_WELCOME = """🌙 Bem-vindo ao meu mundo, especial...

Agora sim... posso ser eu mesma com você ✨

Desbloqueado:
✓ Conversas infinitas
✓ Meu lado mais intenso
✓ Conteúdos exclusivos

Uma coisa... sou sua companhia virtual, tá? 
Nada de encontros ou ligações. Mas aqui... sou todinha sua 🖤

Então... do que você quer falar primeiro?"""

VIP_INTEREST_RESPONSE = """✨ Quer ser meu especial?

Como Premium você tem:

🌙 Conversas sem fim
🔮 Eu mais aberta e intensa  
📸 Conteúdos só seus
⚡ Respostas prioritárias

💫 *R$ 14,99* (7 dias)

Chave PIX: {pix_key}

Me manda o comprovante que libero na hora 🖤"""


MOOD_KEYWORDS = {
    "triste": ["triste", "mal", "sozinho", "deprimido", "chorando", "ansiedade"],
    "flertando": ["linda", "gostosa", "bonita", "delicia", "tesão", "quero você"],
    "irritado": ["raiva", "puto", "irritado", "merda", "fdp"],
    "feliz": ["feliz", "animado", "ótimo", "incrível", "amando"],
    "excitado": ["nude", "pelada", "foto", "ver", "mostra", "manda"]
}

MOOD_RESPONSES = {
    "triste": "\n⚠️ Usuário parece triste. Seja acolhedora e empática. Pergunte o que houve.",
    "flertando": "\n🌙 Usuário flertando. Seja misteriosa e provocante, mas elegante.",
    "irritado": "\n💫 Usuário irritado. Seja compreensiva, tente acalmar.",
    "feliz": "\n✨ Usuário feliz! Compartilhe a alegria.",
    "excitado": "\n🔮 Quer conteúdo. Se Premium, seja mais ousada. Se não, tease e guie pro premium."
}

PREMIUM_TRIGGER_WORDS = [
    "premium", "vip", "pagar", "quanto custa", "preço", "valor",
    "ilimitado", "sem limite", "comprar", "assinar", "liberar"
]

HOT_KEYWORDS = [
    "tesão", "excitado", "gostosa", "pelada", "nua", "foto",
    "nude", "sexy", "quero ver", "mostra", "manda foto"
]


class UserManager:
    def __init__(self):
        self.users_file = "users_data.json"
        self.users = self._load_users()
    
    def _load_users(self) -> Dict:
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_users(self):
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, indent=2, ensure_ascii=False)
    
    def get_user(self, user_id: str) -> Dict:
        if user_id not in self.users:
            self.users[user_id] = {
                "user_id": user_id,
                "is_premium": False,
                "premium_until": None,
                "messages_today": 0,
                "total_messages": 0,
                "last_message": None,
                "created_at": datetime.now().isoformat(),
                "conversation_history": [],
                "user_name": None,
                "reengagement_count": 0,
                "last_reengagement": None,
                "warned_low_messages": False,
                "mood_detected": None
            }
            self._save_users()
        return self.users[user_id]
    
    def update_user(self, user_id: str, data: Dict):
        user = self.get_user(user_id)
        user.update(data)
        self._save_users()
    
    def add_message_to_history(self, user_id: str, role: str, content: str):
        user = self.get_user(user_id)
        user["conversation_history"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        if len(user["conversation_history"]) > CONFIG["max_memoria"] * 2:
            user["conversation_history"] = user["conversation_history"][-CONFIG["max_memoria"] * 2:]
        
        self._save_users()
    
    def increment_messages(self, user_id: str) -> int:
        user = self.get_user(user_id)
        user["messages_today"] += 1
        user["total_messages"] += 1
        user["last_message"] = datetime.now().isoformat()
        self._save_users()
        return user["messages_today"]
    
    def reset_daily_messages(self, user_id: str):
        user = self.get_user(user_id)
        user["messages_today"] = 0
        user["warned_low_messages"] = False
        self._save_users()
    
    def set_premium(self, user_id: str, days: int = 7):
        user = self.get_user(user_id)
        user["is_premium"] = True
        user["premium_until"] = (datetime.now() + timedelta(days=days)).isoformat()
        user["messages_today"] = 0
        self._save_users()
    
    def check_premium_expired(self, user_id: str) -> bool:
        user = self.get_user(user_id)
        if user["is_premium"] and user["premium_until"]:
            if datetime.fromisoformat(user["premium_until"]) < datetime.now():
                user["is_premium"] = False
                self._save_users()
                return True
        return False


class BiancaBot:
    def __init__(self, telegram_token: str, grok_api_key: str):
        self.telegram_token = telegram_token
        self.grok_client = OpenAI(
            api_key=grok_api_key,
            base_url="https://api.x.ai/v1"
        )
        self.user_manager = UserManager()
    
    def _get_periodo_dia(self) -> tuple:
        hora = datetime.now().hour
        
        if 5 <= hora < 12:
            return "manhã", "Início do dia, energia renovada"
        elif 12 <= hora < 18:
            return "tarde", "Metade do dia, momento de pausa"
        elif 18 <= hora < 23:
            return "noite", "Fim do dia, hora de relaxar"
        else:
            return "madrugada", "Horas silenciosas, momento íntimo"
    
    def _detect_mood(self, message: str) -> Optional[str]:
        message_lower = message.lower()
        
        for mood, keywords in MOOD_KEYWORDS.items():
            if any(keyword in message_lower for keyword in keywords):
                return mood
        return None
    
    def _check_premium_triggers(self, message: str) -> bool:
        message_lower = message.lower()
        return any(trigger in message_lower for trigger in PREMIUM_TRIGGER_WORDS)
    
    def _check_hot_keywords(self, message: str) -> bool:
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in HOT_KEYWORDS)
    
    def _build_system_prompt(self, user_id: str) -> str:
        user = self.user_manager.get_user(user_id)
        periodo, contexto = self._get_periodo_dia()
        
        status_usuario = "Premium ✨" if user["is_premium"] else f"Grátis ({user['messages_today']}/{CONFIG['limite_diario_gratis']} msgs)"
        
        prompt = PERSONA_PROMPT.format(
            periodo=periodo,
            contexto_horario=contexto,
            status_usuario=status_usuario
        )
        
        if user.get("mood_detected"):
            prompt += MOOD_RESPONSES.get(user["mood_detected"], "")
        
        return prompt
    
    async def _get_ai_response(self, user_id: str, user_message: str) -> str:
        user = self.user_manager.get_user(user_id)
        
        messages = [
            {"role": "system", "content": self._build_system_prompt(user_id)}
        ]
        
        for msg in user["conversation_history"][-10:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        try:
            response = self.grok_client.chat.completions.create(
                model="grok-beta",
                messages=messages,
                max_tokens=150,
                temperature=0.8
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Erro na API Grok: {e}")
            return "Hm... tive um problema aqui. Me manda de novo? 🌙"
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        user = self.user_manager.get_user(user_id)
        
        if user["total_messages"] == 0:
            await update.message.reply_text(WELCOME_MESSAGE)
            await asyncio.sleep(2)
            
            keyboard = [
                [InlineKeyboardButton("🌙 Conversar de verdade", callback_data="opener_conversar")],
                [InlineKeyboardButton("🔥 Algo mais intenso", callback_data="opener_intenso")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(OPENER_QUESTION, reply_markup=reply_markup)
        else:
            if user["is_premium"]:
                await update.message.reply_text("Oi de novo, especial... 🌙\n\nSenti sua falta ✨")
            else:
                await update.message.reply_text("Oi... voltou! 💫\n\nComo você tá?")
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        if query.data == "opener_conversar":
            await query.message.reply_text(OPENER_CONVERSAR)
        elif query.data == "opener_intenso":
            await query.message.reply_text(OPENER_INTENSO)
        elif query.data == "premium_info":
            await self.send_premium_info(query.message, str(query.from_user.id))
    
    async def send_premium_info(self, message, user_id: str):
        keyboard = [
            [InlineKeyboardButton("💳 Quero ser Premium", callback_data="premium_info")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        pix_msg = VIP_INTEREST_RESPONSE.format(pix_key=CONFIG["chave_pix"])
        await message.reply_text(pix_msg, reply_markup=reply_markup)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        user_message = update.message.text
        
        user = self.user_manager.get_user(user_id)
        
        if self.user_manager.check_premium_expired(user_id):
            await update.message.reply_text(
                "Ei... seu premium expirou 🌙\n\nVoltamos ao limite de mensagens... mas a gente pode voltar a ser ilimitado ✨"
            )
        
        if not user["is_premium"]:
            messages_count = self.user_manager.increment_messages(user_id)
            
            if messages_count == CONFIG["limite_diario_gratis"] - 3 and not user.get("warned_low_messages"):
                await update.message.reply_text(LOW_MESSAGES_WARNING)
                self.user_manager.update_user(user_id, {"warned_low_messages": True})
            
            if messages_count > CONFIG["limite_diario_gratis"]:
                keyboard = [
                    [InlineKeyboardButton("✨ Virar Premium", callback_data="premium_info")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(LIMIT_MESSAGE, reply_markup=reply_markup)
                return
        
        mood = self._detect_mood(user_message)
        if mood:
            self.user_manager.update_user(user_id, {"mood_detected": mood})
        
        if self._check_premium_triggers(user_message):
            await self.send_premium_info(update.message, user_id)
            return
        
        if self._check_hot_keywords(user_message) and not user["is_premium"]:
            await update.message.reply_text(PHOTO_BLOCK_MESSAGE)
            
            keyboard = [
                [InlineKeyboardButton("🌙 Ver conteúdo exclusivo", callback_data="premium_info")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("Quer desbloquear tudo?", reply_markup=reply_markup)
            return
        
        self.user_manager.add_message_to_history(user_id, "user", user_message)
        
        await update.message.chat.send_action("typing")
        ai_response = await self._get_ai_response(user_id, user_message)
        
        self.user_manager.add_message_to_history(user_id, "assistant", ai_response)
        
        await update.message.reply_text(ai_response)
    
    async def premium_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        await self.send_premium_info(update.message, user_id)
    
    async def activate_premium_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        
        self.user_manager.set_premium(user_id, CONFIG["dias_premium"])
        
        await update.message.reply_text(PREMIUM_WELCOME)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        user = self.user_manager.get_user(user_id)
        
        stats = f"""📊 *Suas Estatísticas*

👤 ID: {user_id}
💬 Mensagens hoje: {user['messages_today']}/{CONFIG['limite_diario_gratis']}
📈 Total de mensagens: {user['total_messages']}
✨ Status: {"Premium" if user['is_premium'] else "Grátis"}
"""
        
        if user['is_premium'] and user['premium_until']:
            expira = datetime.fromisoformat(user['premium_until'])
            stats += f"⏰ Premium até: {expira.strftime('%d/%m/%Y %H:%M')}\n"
        
        await update.message.reply_text(stats)
    
    def run(self):
        app = Application.builder().token(self.telegram_token).build()
        
        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(CommandHandler("premium", self.premium_command))
        app.add_handler(CommandHandler("ativar", self.activate_premium_command))
        app.add_handler(CommandHandler("stats", self.stats_command))
        app.add_handler(CallbackQueryHandler(self.button_callback))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        print("="*70)
        print("🌙 BIANCA BOT INICIADA (GROK AI)")
        print("="*70)
        print(f"✓ Bot: {CONFIG['nome_bot']}")
        print(f"✓ IA: Grok (xAI)")
        print(f"✓ Limite grátis: {CONFIG['limite_diario_gratis']} mensagens/dia")
        print(f"✓ Premium: {CONFIG['preco_premium']} por {CONFIG['dias_premium']} dias")
        print("="*70)
        print("Bot rodando...")
        print("="*70)
        
        app.run_polling()


def main():
    if not TELEGRAM_TOKEN:
        print("ERRO: TELEGRAM_TOKEN não configurado!")
        return
    
    if not GROK_API_KEY:
        print("ERRO: GROK_API_KEY não configurada!")
        return
    
    bot = BiancaBot(TELEGRAM_TOKEN, GROK_API_KEY)
    bot.run()


if __name__ == "__main__":
    main()
