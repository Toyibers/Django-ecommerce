import requests
from django.conf import settings

def send_telegram_message(chat_id, message):
    bot_token = settings.TELEGRAM_BOT_TOKEN
    telegram_api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
    requests.post(telegram_api_url, data=payload)