import requests
from config import *

product_id = 2729028995

headers = {
    'Content-Type': 'application/json; charset=utf-8',
    'Api-Key': API_KEY,
    'Client-Id': CLIENT_ID,
}

params = {
    "product_id": product_id,
}

response = requests.post(urls_find_tovar, json=params, headers=headers)

print(response.json())
