import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_embeddings(text_list):
    url = 'https://api.jina.ai/v1/embeddings'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {os.getenv("JINA_AI_API")}'
    }
    data = {
        'model': 'jina-embeddings-v3',
        'dimensions': 1024,
        'normalized': True,
        'embedding_type': 'float',
        'input': text_list
    }
    res = requests.post(url, headers=headers, json=data)
    if res.status_code != 200:
        raise Exception(f"Jina API error: {res.status_code}, {res.text}")

    res_json = res.json()
    print('END --> get embeddings')  # Debug output

    return [item["embedding"] for item in res_json.get("data", [])]