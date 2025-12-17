import os
import json
import requests

# === НАСТРОЙКИ ===
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
YANDEX_API_KEY = os.environ.get("YANDEX_API_KEY")
FOLDER_ID = os.environ.get("FOLDER_ID")

YANDEX_GPT_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

SYSTEM_PROMPT = """
Ты — профессиональный диетолог.
Твоя задача — составлять рацион питания по калорийности,
подбирать рецепты, рассчитывать БЖУ и ориентировочную стоимость блюд.

Всегда сначала уточняй:
- возраст
- пол
- рост
- вес
- уровень физической активности
- цель (похудение / поддержание / набор)

Если данных нет — предложи обзорный рацион и объясни,
что для точных расчётов нужны параметры.
"""

# === TELEGRAM ===
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": chat_id,
        "text": text
    })


# === CLOUD FUNCTION ENTRY POINT ===
def handler(event, context):
    try:
        body = json.loads(event["body"])
        message = body.get("message", {})
        text = message.get("text")
        chat_id = message.get("chat", {}).get("id")

        if not text or not chat_id:
            return {"statusCode": 200, "body": "ok"}

        # /start
        if text == "/start":
            send_message(
                chat_id,
                "Привет! Я Диетолог 24/7 😊\n\n"
                "Я помогу составить рацион, рассчитать калории и БЖУ.\n"
                "Напиши, с какой целью ты хочешь питание."
            )
            return {"statusCode": 200, "body": "ok"}

        headers = {
            "Authorization": f"Api-Key {YANDEX_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "modelUri": f"gpt://{FOLDER_ID}/yandexgpt/5.1-pro",
            "completionOptions": {
                "stream": False,
                "temperature": 0.4,
                "maxTokens": 1500
            },
            "messages": [
                {"role": "system", "text": SYSTEM_PROMPT},
                {"role": "user", "text": text}
            ]
        }

        response = requests.post(
            YANDEX_GPT_URL,
            headers=headers,
            json=payload,
            timeout=10
        )

        result = response.json()
        answer = result["result"]["alternatives"][0]["message"]["text"]

        send_message(chat_id, answer)

        return {"statusCode": 200, "body": "ok"}

    except Exception as e:
        print("ERROR:", str(e))
        return {"statusCode": 200, "body": "error"}
