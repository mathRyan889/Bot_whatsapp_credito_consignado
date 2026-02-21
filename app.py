import re
import logging
from flask import Flask, request, jsonify
from typing import Optional, Dict, Any

# Mock das suas classes internas para manter a estrutura
from bot.ai_bot import AIBot
from services.waha import Waha

# --- CONFIGURAÇÕES E CONSTANTES ---
CONFIG = {
    # Lista de números autorizados (Suporte)
    "NUMEROS_SUPORTE": ["215470020018431", "556282027373", "6282027373"], 
    "PORTA": 5050,
    "TAG_SIMULACAO": "|||SUPORTE_ALERT:",
    "TAG_FECHAMENTO": "|||FECHAMENTO_ALERT:",
    "GATILHO_SIMULACAO": "Vou verificar a melhor proposta",
    "GATILHO_FECHAMENTO": "Já encaminhei para o nosso financeiro"
}

# --- REGEX OTIMIZADOS ---
REGEX_DADOS = {
    "CPF": re.compile(r"(?:CPF|cpf)\s*:?\s*([\d.-]+)"),
    "TEL": re.compile(r"(?:TEL|Telefone|id)\s*:?\s*(\d+)", re.I),
    "VALOR": re.compile(r"(?:VALOR|R\$)\s*:?\s*([\d.,]+)", re.I),
    "AGENCIA": re.compile(r"(?:Ag|Agência)\.?\s*:?\s*([\d\-]{3,})", re.I),
    "CONTA": re.compile(r"(?:Conta|Cc|C/C)\.?\s*:?\s*([\d\-]{4,})", re.I),
    "BANCO": re.compile(r"Banco\s*:?\s*([A-Za-z0-9\s]+)", re.I)
}

# Configuração de Log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("App")

app = Flask(__name__)
waha = Waha()
bot = AIBot()

# --- UTILITÁRIOS ---

def extrair_valor(regex_key: str, texto: str) -> Optional[str]:
    """Retorna o valor extraído ou None se falhar."""
    match = REGEX_DADOS[regex_key].search(texto)
    return match.group(1).strip() if match else None

def limpar_tags(texto: str) -> str:
    """Remove tags de controle da IA para que o cliente não as veja."""
    return re.sub(r'\|\|\|.*?(\|\|\||$)', '', texto).strip()

# --- LÓGICA DE NEGÓCIO ---

def processar_comando_suporte(chat_id: str, body: str, sender_id: str) -> bool:
    """Processa comandos que o suporte envia para ofertar valores ao cliente."""
    cpf = extrair_valor("CPF", body)
    tel = extrair_valor("TEL", body)
    valor = extrair_valor("VALOR", body)

    # Fallback: tenta separar por vírgula se o regex falhar
    if not all([cpf, tel, valor]):
        partes = [p.strip() for p in body.split(',')]
        if len(partes) >= 3:
            cpf, tel, valor = partes[0], partes[1], partes[2]

    if cpf and tel and valor:
        tel_limpo = re.sub(r'\D', '', tel)
        
        # Verifica se é LID (ID longo) ou número comum
        if len(tel_limpo) > 14:
             suffix = "@lid"
        else:
             suffix = "@c.us"
             
        cliente_chat_id = f"{tel_limpo}{suffix}"
        
        logger.info(f"🎯 Oferta detectada de {sender_id} para: {cliente_chat_id}")

        msg_oferta = (
            f"Boas notícias! 🎉\n\n"
            f"Consegui a liberação aqui. Tem disponível para você o valor de "
            f"*R$ {valor}* para cair hoje mesmo na sua conta.\n\n"
            f"Podemos seguir com a contratação?"
        )

        waha.send_message(cliente_chat_id, msg_oferta)
        waha.send_message(chat_id, f"✅ Oferta de R$ {valor} enviada para {tel_limpo}!")
        return True
    
    waha.send_message(chat_id, "⚠️ Dados incompletos. Envie: CPF, Telefone, Valor")
    return False

def tratar_fluxo_ia(chat_id: str, response: str, sender_id: str):
    """Encaminha a resposta da IA e dispara alertas para o suporte."""
    # Envia alerta para o primeiro número da lista de suporte configurada
    id_suporte = f"{CONFIG['NUMEROS_SUPORTE'][0]}@lid" # Ou @c.us dependendo do seu suporte
    msg_limpa = limpar_tags(response)

    # 1. Fluxo de Simulação
    if CONFIG['TAG_SIMULACAO'] in response or CONFIG['GATILHO_SIMULACAO'] in response:
        tag_match = re.search(f"{re.escape(CONFIG['TAG_SIMULACAO'])}(.*?)(?:\|\|\||$)", response)
        dados = tag_match.group(1).strip() if tag_match else "Consultar histórico."
        
        waha.send_message(chat_id, msg_limpa)
        waha.send_message(id_suporte, f"🚨 *SIMULAÇÃO*\n📝 Dados: {dados}\n📱 Cliente: {sender_id}")

    # 2. Fluxo de Fechamento (AGORA COM DADOS BANCÁRIOS COMPLETOS)
    elif CONFIG['TAG_FECHAMENTO'] in response or CONFIG['GATILHO_FECHAMENTO'] in response:
        # Extrai os dados da resposta da IA
        banco = extrair_valor("BANCO", response) or "Não detectado"
        agencia = extrair_valor("AGENCIA", response) or "---"
        conta = extrair_valor("CONTA", response) or "---"

        waha.send_message(chat_id, msg_limpa)
        
        # Monta mensagem detalhada para o suporte
        msg_suporte = (
            f"💰 *FECHAMENTO DETECTADO*\n\n"
            f"🏦 *Banco:* {banco}\n"
            f"🏢 *Agência:* {agencia}\n"
            f"💳 *Conta:* {conta}\n"
            f"📱 *Cliente:* {sender_id}\n\n"
            f"✅ *Ação:* Proceder com o pagamento."
        )
        waha.send_message(id_suporte, msg_suporte)

    # 3. Resposta Normal
    else:
        waha.send_message(chat_id, msg_limpa)

# --- ROTAS ---

@app.route('/chatbot/webhook/', methods=['POST'])
def webhook():
    try:
        data = request.get_json(silent=True)
        if not data or 'payload' not in data:
            return jsonify({'status': 'error'}), 400

        payload = data['payload']
        chat_id = payload.get('from')
        body = payload.get('body', '').strip()
        
        if not chat_id or not body or '@g.us' in chat_id:
            return jsonify({'status': 'ignored'}), 200

        sender_id = chat_id.split('@')[0]
        logger.info(f"📩 Webhook: {sender_id} | ChatID: {chat_id}")

        # Rota Suporte
        if sender_id in CONFIG["NUMEROS_SUPORTE"]:
            if processar_comando_suporte(chat_id, body, sender_id):
                return jsonify({'status': 'ok', 'origin': 'support'}), 200
            return jsonify({'status': 'support_command_failed'}), 200

        # Rota Cliente
        logger.info(f"💬 Mensagem de Cliente: {sender_id}")
        waha.start_typing(chat_id)
        try:
            history = waha.get_history_messages(chat_id, limit=10)
            ai_response = bot.invoke(history, body)
            tratar_fluxo_ia(chat_id, ai_response, sender_id)
        finally:
            waha.stop_typing(chat_id)

        return jsonify({'status': 'ok'}), 200

    except Exception as e:
        logger.error(f"❌ Erro Webhook: {e}", exc_info=True)
        return jsonify({'status': 'error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=CONFIG["PORTA"])