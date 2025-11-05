import os
from datetime import datetime
from pathlib import Path


REQUISITES_DIR = Path("reqv_files")
USER_DATA_DIR = Path("data")


def save_req_txt(user_data, data: dict) -> str:
    REQUISITES_DIR.mkdir(exist_ok=True) 
    
    file_name = f"{user_data.id}_req.txt"
    file_path = REQUISITES_DIR / file_name
    
    user_url = f"tg://user?id={user_data.id}"

    requisites_info = f"User ID: {user_data.id}\n"
    if user_data.username:
        requisites_info += f"Username: @{user_data.username}\n"
    else:
        requisites_info += f"Ссылка (по ID): {user_url}\n"

    requisites_info += "-" * 30 + "\n"
    requisites_info += f"Страна/Тип: {data.get('country', 'N/A')}\n"
    requisites_info += f"Банк: {data.get('bank', 'N/A')}\n"
    requisites_info += f"Номер карты/Кошелек: {data.get('card_number', 'N/A')}\n"
    
    if data.get('country') == "TON":
        requisites_info += f"Адрес TON: {data.get('requisites', 'N/A')}\n"
    
    requisites_info += f"Телефон: {data.get('phone', 'N/A')}\n"
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(requisites_info)

    return str(file_path)


def save_user(user_id, full_name):
    USER_DATA_DIR.mkdir(exist_ok=True)
    filename = USER_DATA_DIR / f"{user_id}.txt"
    created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"ID: {user_id}\n")
        f.write(f"Full Name: {full_name}\n")
        f.write(f"Первый запуск бота: {created}\n")

    return str(filename)

def get_req(user_id) -> str | None:
    file_name = f"{user_id}_req.txt"
    file_path = REQUISITES_DIR / file_name
    
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return None