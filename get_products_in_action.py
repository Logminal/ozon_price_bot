import requests
import json
from config import *
from get_actions import *
from telegram_notify import send_telegram_message


headers = {
    'Content-Type': 'application/json; charset=utf-8',
    'Api-Key': API_KEY,
    'Client-Id': CLIENT_ID,
}

def get_products_in_actions():
    count = 0
    products_in_action = []
    for action in ids_actions:
        current_last_id = None
        last_id = None

        while True:
            # 1. Готовим запрос
            params = {
                "action_id": action['action_id'],
                "limit": 100
            }
            if last_id is not None:
                params["last_id"] = last_id

            response = requests.post(urls_get_product_in_actions, json=params, headers=headers)
            data = response.json()

            products = data["result"]["products"]
            total_on_page = len(products)


            products_in_action.extend(products)

            if total_on_page < 100:
                break
            else:
                last_id = data["result"]["last_id"]
    return products_in_action


def calc_price_for_action(action_id):
    products_in_action = []
    last_id = None

    while True:
        params = {
            "action_id": action_id,
            "limit": 100
        }
        if last_id is not None:
            params["last_id"] = last_id

        response = requests.post(urls_get_product_in_actions, json=params, headers=headers)
        data = response.json()
        products = data["result"]["products"]
        products_in_action.extend(products)

        if len(products) < 100:
            break
        else:
            last_id = data["result"]["last_id"]

    products_big_action = []
    for product in products_in_action:
        calc_price_procent = product['price'] * 0.69  # = 69% от полной → скидка 31%
        if calc_price_procent <= product['action_price']:
            continue
        else:
            products_big_action.append(product['id'])

    return products_big_action


def find_tovar(products):
    names = []
    for product_id in products:
        params = {
            "product_id": product_id,
        }
        response = requests.post(urls_find_tovar, json=params, headers=headers)
        names.append({
            'id': response.json()['result']['id'],
            'name': response.json()['result']['name'],
        })
    return names

def delete_products_action():
    all_messages = []

    for action in ids_actions:
        action_id = action['action_id']
        action_title = action['title']

        product_ids_to_remove = calc_price_for_action(action_id)

        if not product_ids_to_remove:
            message = f"✅ Акция: <b>{action_title}</b>\n✔️ Товаров со скидкой >30% — нет. Всё в норме 👌"
            print(message)
            all_messages.append(message)
            continue

        names_info = find_tovar(product_ids_to_remove)

        params = {
            'action_id': action_id,
            'product_ids': product_ids_to_remove
        }
        response = requests.post(delete_tovar_in_action, json=params, headers=headers)
        result = response.json()['result']

        success_ids = set(result['product_ids'])
        rejected_ids = {item['product_id'] for item in result['rejected']}

        success_names = [item['name'] for item in names_info if item['id'] in success_ids]
        rejected_names = [item['name'] for item in names_info if item['id'] in rejected_ids]

        message_lines = [
            f"✅ Удаление из акции: <b>{action_title}</b>",
            f"✔️ Удалено: {len(success_names)} шт.",
        ]

        if success_names:
            message_lines.append("📦 Удалённые товары:")
            message_lines.extend(f"– {name}" for name in success_names)

        if rejected_names:
            message_lines.append(f"\n❌ Не удалено: {len(rejected_names)} шт.")
            message_lines.append("⚠️ Причины (примеры):")
            for item in result['rejected'][:3]:
                reason = item.get('reason', 'неизвестно')
                prod_id = item.get('product_id')
                name = next((n['name'] for n in names_info if n['id'] == prod_id), f"ID{prod_id}")
                message_lines.append(f"– {name} → {reason}")
            if len(result['rejected']) > 3:
                message_lines.append(f"... и ещё {len(result['rejected']) - 3} шт.")

        message = "\n".join(message_lines)
        print(message)
        all_messages.append(message)

    full_report = "\n\n" + ("—" * 40) + "\n\n".join(all_messages)
    send_telegram_message(full_report)
# v3_Райли_26329