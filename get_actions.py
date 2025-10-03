import requests
import json
from config import *

headers = {
    'Content-Type': 'application/json; charset=utf-8',
    'Api-Key': API_KEY,
    'Client-Id': CLIENT_ID,
}

response = requests.get(urls_get_action, headers=headers)
action_ozon = response.json()
ids_actions = []
for item in action_ozon['result']:
    if item['participating_products_count'] != 0:
        array = {
            'action_id': item["id"],
            'title': item["title"],
        }
        ids_actions.append(array)


# print(ids_actions)
