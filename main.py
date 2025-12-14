import os
import requests
from flask import Flask, request

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

app = Flask(__name__)

def send_message(chat_id, text):
    requests.post(
        f"{TELEGRAM_API_URL}/sendMessage",
        json={"chat_id": chat_id, "text": text}
    )

def ask_openai(message):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ]
    }
    response = requests.post(OPENAI_API_URL, headers=headers, json=payload)
    return response.json()["choices"][0]["message"]["content"]

@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    chat_id = data["message"]["chat"]["id"]
    text = data["message"]["text"]
    reply = ask_openai(text)
    send_message(chat_id, reply)
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
