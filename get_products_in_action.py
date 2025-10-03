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
    products_in_action = []  # сюда будем складывать ВСЕ товары
    for action in ids_actions:
        current_last_id = None
        last_id = None  # сначала мы ничего не брали — поэтому None

        while True:
            # 1. Готовим запрос
            params = {
                "action_id": action['action_id'],
                "limit": 100
            }
            if last_id is not None:
                params["last_id"] = last_id  # добавляем, только если есть

            # 2. Отправляем запрос
            response = requests.post(urls_get_product_in_actions, json=params, headers=headers)
            data = response.json()

            # 3. Смотрим, что пришло
            products = data["result"]["products"]
            total_on_page = len(products)

            # 4. Складываем товары в общую коробку
            products_in_action.extend(products)

            # 5. Проверяем: закончились ли товары?
            if total_on_page < 100:
                break  # если меньше 100 — это последняя пачка
            else:
                # иначе — запоминаем last_id для следующего запроса
                last_id = data["result"]["last_id"]
    # print(products_in_action)
    return products_in_action

get_products_in_actions()


def calc_price():
    products_in_action = get_products_in_actions()
    products_big_action = []
    for product in products_in_action:
        calc_price_procent = product['price'] * 0.69
        if calc_price_procent <= product['action_price']:
            continue
        else:
            # print(f"пос: {calc_price_procent} ------- цена озон: {product['action_price']}")
            # print(calc_price_procent == action['action_price'])
            # print(f"ID товара {product['id']}.Скидка товара больше 30%")
            products_big_action.append(product['id'])

    return products_big_action


def delete_products_action():
    products = calc_price()
    id_action = ''
    for action in ids_actions:
        id_action = action['action_id']

        if len(products) >0:
            params = {
                'action_id': id_action,
                'product_ids': products
            }
            response = requests.post(delete_tovar_in_action, json=params, headers=headers)
            # print(response.json())

            result = response.json()['result']
            success_count = len(result['product_ids'])
            rejected_count = len(result['rejected'])
            total_requested = len(params['product_ids'])
            message = (
                f"✅ Удаление из акции: <b>{action['title']}</b>\n"
                f"📦 Запрошено: {total_requested}\n"
                f"✔️ Удалено: {success_count}\n"
                f"❌ Не удалено: {rejected_count}"
            )
            if result['rejected']:
                message += f"\n⚠️ Не удалено: {len(result['rejected'])} шт."
        else:
            message = "Все супер✅ На все товары акция 30%👌"

        send_telegram_message(message)

        # print(message)
