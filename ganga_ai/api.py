import requests
import json
from ganga_ai.config import config

def backend_query(query: str):
    url = f"{config.backend_url.rstrip('/')}/rag/query"
    payload = {
        "query": query,
        "user_id": config.user_id
    }

    response = requests.post(
        url,
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
        timeout=30
    )

    return response.json()
