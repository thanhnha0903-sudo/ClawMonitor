import requests

TELEGRAM_BOT_TOKEN = '8721014265:AAGXi2Ze82L1a-uEwKwljMF31DBCJwY5R3s'

def send_telegram_alert(message, chat_id):
    if not TELEGRAM_BOT_TOKEN or not chat_id:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Telegram Error: {e}")
