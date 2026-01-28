"""
═══════════════════════════════════════════════════════════════════════════
🌙 BIANCA BOT - TELEGRAM + IA COMPLETO
═══════════════════════════════════════════════════════════════════════════

Bot de Companhia Virtual com IA (Claude/Anthropic)
Sistema de Assinatura Premium Integrado

ARQUIVO ÚNICO - TUDO EM UM SÓ LUGAR!

═══════════════════════════════════════════════════════════════════════════
📋 INSTRUÇÕES DE USO
═══════════════════════════════════════════════════════════════════════════

OPÇÃO 1 - LOCAL (SEU COMPUTADOR):
1. Instale: pip install python-telegram-bot anthropic
2. Configure os tokens abaixo (linhas 70-71)
3. Execute: python bianca_bot_unificado.py
4. No Telegram, procure seu bot e digite /start

OPÇÃO 2 - DEPLOY NO RAILWAY (24/7 NA NUVEM):
1. Crie conta no Railway (railway.app)
2. New Project → Empty Project
3. Faça upload deste arquivo (bianca_bot_unificado.py)
4. Crie arquivo "requirements.txt" com:
   python-telegram-bot==20.7
   anthropic==0.39.0
5. Crie arquivo "Procfile" com:
   worker: python bianca_bot_unificado.py

6. No Railway, configure:
   
   ⚙️ A) VARIÁVEIS (Variables):
      Adicione estas 2 variáveis:
      
      Nome: TELEGRAM_TOKEN
      Valor: seu_token_do_botfather
      
      Nome: ANTHROPIC_API_KEY
      Valor: sua_chave_anthropic
   
   🚀 B) START COMMAND:
      Vá em: Settings → Deploy → Start Command
      Cole exatamente: python bianca_bot_unificado.py
      Salve e faça Redeploy
      
7. Deploy automático!

═══════════════════════════════════════════════════════════════════════════
🚨 IMPORTANTE - COMANDO DE START PARA O RAILWAY:
═══════════════════════════════════════════════════════════════════════════

Copie este comando e cole no Railway (Settings → Deploy → Start Command):

python bianca_bot_unificado.py

═══════════════════════════════════════════════════════════════════════════

OBTENDO AS CREDENCIAIS:
- Telegram Token: https://t.me/BotFather → /newbot
- Anthropic API: https://console.anthropic.com/ → API Keys

═══════════════════════════════════════════════════════════════════════════
✨ FUNCIONALIDADES INCLUÍDAS
═══════════════════════════════════════════════════════════════════════════

✅ IA Conversacional (Claude) com personalidade enigmática
✅ Sistema Premium (R$ 14,99/7 dias)
✅ Limite Grátis (10 mensagens/dia)
✅ Detecção de Humor do usuário
✅ Gatilhos de Conversão inteligentes
✅ Paywall para Conteúdo exclusivo
✅ Memória de Conversas (15 mensagens)
✅ Sistema de estatísticas
✅ Suporte a variáveis de ambiente (Railway)

COMANDOS DISPONÍVEIS:
/start - Inicia conversa
/premium - Info sobre assinatura
/ativar - Ativa premium (teste)
/stats - Suas estatísticas

═══════════════════════════════════════════════════════════════════════════
"""

import os
import json
import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Imports do Telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# API da Anthropic (Claude)
import anthropic


# ═══════════════════════════════════════════════════════════════════════════
# 🔑 CONFIGURAÇÃO - EDITE AQUI OU USE VARIÁVEIS DE AMBIENTE
# ═══════════════════════════════════════════════════════════════════════════

# Para uso local: edite diretamente aqui
# Para Railway: deixe "" e configure nas variáveis de ambiente
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# Se não usar variáveis de ambiente, descomente e configure abaixo:
# TELEGRAM_TOKEN = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
# ANTHROPIC_API_KEY = "sk-ant-api03-xxxxxxxxxxxxx"


# ═══════════════════════════════════════════════════════════════════════════
# ⚙️ CONFIGURAÇÕES GERAIS
# ═══════════════════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════════════════
# 🎭 PERSONA E PROMPT DA IA
# ═══════════════════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════════════════
# 💬 MENSAGENS DO SISTEMA
# ═══════════════════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════════════════
# 🎯 KEYWORDS PARA DETECÇÃO
# ═══════════════════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════════════════
# 💾 GERENCIAMENTO DE USUÁRIOS
# ═══════════════════════════════════════════════════════════════════════════

class UserManager:
    """Gerencia dados dos usuários"""
    
    def __init__(self):
        self.users_file = "users_data.json"
        self.users = self._load_users()
    
    def _load_users(self) -> Dict:
        """Carrega dados dos usuários do arquivo"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_users(self):
        """Salva dados dos usuários no arquivo"""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, indent=2, ensure_ascii=False)
    
    def get_user(self, user_id: str) -> Dict:
        """Retorna dados do usuário"""
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
        """Atualiza dados do usuário"""
        user = self.get_user(user_id)
        user.update(data)
        self._save_users()
    
    def add_message_to_history(self, user_id: str, role: str, content: str):
        """Adiciona mensagem ao histórico"""
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
        """Incrementa contador de mensagens"""
        user = self.get_user(user_id)
        user["messages_today"] += 1
        user["total_messages"] += 1
        user["last_message"] = datetime.now().isoformat()
        self._save_users()
        return user["messages_today"]
    
    def reset_daily_messages(self, user_id: str):
        """Reseta contador diário"""
        user = self.get_user(user_id)
        user["messages_today"] = 0
        user["warned_low_messages"] = False
        self._save_users()
    
    def set_premium(self, user_id: str, days: int = 7):
        """Define usuário como premium"""
        user = self.get_user(user_id)
        user["is_premium"] = True
        user["premium_until"] = (datetime.now() + timedelta(days=days)).isoformat()
        user["messages_today"] = 0
        self._save_users()
    
    def check_premium_expired(self, user_id: str) -> bool:
        """Verifica se premium expirou"""
        user = self.get_user(user_id)
        if user["is_premium"] and user["premium_until"]:
            if datetime.fromisoformat(user["premium_until"]) < datetime.now():
                user["is_premium"] = False
                self._save_users()
                return True
        return False


# ═══════════════════════════════════════════════════════════════════════════
# 🤖 BOT PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════

class BiancaBot:
    """Bot principal com IA"""
    
    def __init__(self, telegram_token: str, anthropic_api_key: str):
        self.telegram_token = telegram_token
        self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
        self.user_manager = UserManager()
    
    def _get_periodo_dia(self) -> tuple:
        """Retorna período do dia e contexto"""
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
        """Detecta humor do usuário"""
        message_lower = message.lower()
        
        for mood, keywords in MOOD_KEYWORDS.items():
            if any(keyword in message_lower for keyword in keywords):
                return mood
        return None
    
    def _check_premium_triggers(self, message: str) -> bool:
        """Verifica gatilhos de premium"""
        message_lower = message.lower()
        return any(trigger in message_lower for trigger in PREMIUM_TRIGGER_WORDS)
    
    def _check_hot_keywords(self, message: str) -> bool:
        """Verifica keywords quentes"""
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in HOT_KEYWORDS)
    
    def _build_system_prompt(self, user_id: str) -> str:
        """Constrói prompt do sistema"""
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
        """Obtém resposta da IA"""
        user = self.user_manager.get_user(user_id)
        
        messages = []
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
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=150,
                system=self._build_system_prompt(user_id),
                messages=messages
            )
            
            return response.content[0].text
        except Exception as e:
            print(f"Erro na API: {e}")
            return "Hm... tive um problema aqui. Me manda de novo? 🌙"
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler do /start"""
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
        """Handler para botões"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "opener_conversar":
            await query.message.reply_text(OPENER_CONVERSAR)
        elif query.data == "opener_intenso":
            await query.message.reply_text(OPENER_INTENSO)
        elif query.data == "premium_info":
            await self.send_premium_info(query.message, str(query.from_user.id))
    
    async def send_premium_info(self, message, user_id: str):
        """Envia informações premium"""
        keyboard = [
            [InlineKeyboardButton("💳 Quero ser Premium", callback_data="premium_info")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        pix_msg = VIP_INTEREST_RESPONSE.format(pix_key=CONFIG["chave_pix"])
        await message.reply_text(pix_msg, reply_markup=reply_markup)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler principal de mensagens"""
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
        """Handler do /premium"""
        user_id = str(update.effective_user.id)
        await self.send_premium_info(update.message, user_id)
    
    async def activate_premium_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler do /ativar"""
        user_id = str(update.effective_user.id)
        
        self.user_manager.set_premium(user_id, CONFIG["dias_premium"])
        
        await update.message.reply_text(PREMIUM_WELCOME)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler do /stats"""
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
        """Inicia o bot"""
        app = Application.builder().token(self.telegram_token).build()
        
        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(CommandHandler("premium", self.premium_command))
        app.add_handler(CommandHandler("ativar", self.activate_premium_command))
        app.add_handler(CommandHandler("stats", self.stats_command))
        app.add_handler(CallbackQueryHandler(self.button_callback))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        print("="*70)
        print("🌙 BIANCA BOT INICIADA")
        print("="*70)
        print(f"✓ Bot: {CONFIG['nome_bot']}")
        print(f"✓ Limite grátis: {CONFIG['limite_diario_gratis']} mensagens/dia")
        print(f"✓ Premium: {CONFIG['preco_premium']} por {CONFIG['dias_premium']} dias")
        print("="*70)
        print("Bot rodando... Pressione Ctrl+C para parar")
        print("="*70)
        
        app.run_polling()


# ═══════════════════════════════════════════════════════════════════════════
# 🚀 EXECUÇÃO PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════

def main():
    """Função principal"""
    
    # Validação
    if not TELEGRAM_TOKEN:
        print("="*70)
        print("❌ ERRO: TELEGRAM_TOKEN não configurado!")
        print("="*70)
        print()
        print("Configure o token de uma dessas formas:")
        print()
        print("OPÇÃO 1 - Direto no código (linha 71):")
        print('  TELEGRAM_TOKEN = "123456789:ABCdef..."')
        print()
        print("OPÇÃO 2 - Variável de ambiente:")
        print("  export TELEGRAM_TOKEN=123456789:ABCdef...")
        print()
        print("OPÇÃO 3 - Railway:")
        print("  Variables → TELEGRAM_TOKEN")
        print()
        print("Obtenha em: https://t.me/BotFather")
        print("="*70)
        return
    
    if not ANTHROPIC_API_KEY:
        print("="*70)
        print("❌ ERRO: ANTHROPIC_API_KEY não configurada!")
        print("="*70)
        print()
        print("Configure a chave de uma dessas formas:")
        print()
        print("OPÇÃO 1 - Direto no código (linha 72):")
        print('  ANTHROPIC_API_KEY = "sk-ant-api03-..."')
        print()
        print("OPÇÃO 2 - Variável de ambiente:")
        print("  export ANTHROPIC_API_KEY=sk-ant-api03-...")
        print()
        print("OPÇÃO 3 - Railway:")
        print("  Variables → ANTHROPIC_API_KEY")
        print()
        print("Obtenha em: https://console.anthropic.com/")
        print("="*70)
        return
    
    # Inicia bot
    print()
    print("✅ Credenciais configuradas")
    print(f"✅ Token Telegram: {TELEGRAM_TOKEN[:10]}...")
    print(f"✅ API Key Anthropic: {ANTHROPIC_API_KEY[:15]}...")
    print()
    
    bot = BiancaBot(TELEGRAM_TOKEN, ANTHROPIC_API_KEY)
    bot.run()


if __name__ == "__main__":
    main()


