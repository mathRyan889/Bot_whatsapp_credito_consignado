import os
import requests
import logging

class Waha:
    def __init__(self):
        # Pega a URL ou usa o nome do container como default
        self.__api_url = os.getenv('WAHA_API_URL', 'http://waha:3000')
        self.__api_key = os.getenv('WAHA_API_KEY')
        self.session = requests.Session()
        
        # Configura headers padrão para todas as requisições
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-Api-Key': self.__api_key or '',
        })
        
        self.logger = logging.getLogger(__name__)

    def _post(self, endpoint, payload):
        """Helper interno para POST com tratamento de erro básico"""
        url = f'{self.__api_url}{endpoint}'
        try:
            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro Waha POST {endpoint}: {e}")
            return None

    def send_message(self, chat_id: str, message: str) -> None:
        payload = {
            'session': 'default',
            'chatId': chat_id,
            'text': message,
        }
        self._post('/api/sendText', payload)

    def get_history_messages(self, chat_id: str, limit: int = 10) -> list:
        url = f'{self.__api_url}/api/default/chats/{chat_id}/messages'
        params = {'limit': limit, 'downloadMedia': 'false'}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro ao buscar histórico: {e}")
        
        return []

    def start_typing(self, chat_id: str) -> None:
        self._post('/api/startTyping', {'session': 'default', 'chatId': chat_id})

    def stop_typing(self, chat_id: str) -> None:
        self._post('/api/stopTyping', {'session': 'default', 'chatId': chat_id})