import requests

MODEL_URI = "gpt://b1g0770l46jbre3bq9ks/yandexgpt-lite"
API_KEY = "AQVN3MI7ekH1ekVGZe_6kp4DW27WNjlFfQmf8rTh"
URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Api-Key {API_KEY}"}

async def Text_Yan(question):
    promt = {
        "modelUri": MODEL_URI,
        "completionOptions": {
            "stream": False,
            "temperature": 1,
            "maxTokens": "2000"
        },
        "messages": [
            {
                "role": "assistant",
                "text": question
            }
        ]
    }

    response = requests.post(URL, headers=HEADERS, json=promt)
    if response.status_code == 200:
        result = response.json()
        try:
            answer = result['result']['alternatives'][0]['message']['text']
            answer = answer.replace("**", "*")
            return f"{answer}"
        except (KeyError, IndexError):
            print("Не удалось получить ответ от YandexGPT.")
    else:
        return False