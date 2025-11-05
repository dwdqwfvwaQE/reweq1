import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

ANKETA_DIR = Path("ankety")
ANKETA_DIR.mkdir(exist_ok=True)

def get_next_anketa_id() -> int:
    try:
        files = [f for f in ANKETA_DIR.iterdir() if f.suffix == '.json']
        if not files:
            return 1
        
        max_id = max(int(f.stem.split('_')[1]) for f in files if f.stem.startswith('anketa_'))
        return max_id + 1
    except Exception:
        return 1

def save_anketa(user_id: int, user_name: str, anketa_text: str) -> Dict[str, Any]:
    anketa_id = get_next_anketa_id()
    
    data = {
        "id": anketa_id,
        "user_id": user_id,
        "username": user_name,
        "text": anketa_text,
        "status": "Открыт",
        "owner_status": "Не передана",
        "timestamp": os.path.getmtime(ANKETA_DIR)
    }
    
    file_path = ANKETA_DIR / f"anketa_{anketa_id}.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    return data

def get_anketa(anketa_id: int) -> Optional[Dict[str, Any]]:
    file_path = ANKETA_DIR / f"anketa_{anketa_id}.json"
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def upd_ank(anketa_id: int, status_key: str, value: str):
    data = get_anketa(anketa_id)
    if data:
        data[status_key] = value
        file_path = ANKETA_DIR / f"anketa_{anketa_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    return False

def delete_anketa(anketa_id: int) -> bool:
    file_path = ANKETA_DIR / f"anketa_{anketa_id}.json"
    if file_path.exists():
        os.remove(file_path)
        return True
    return False

def get_a_ids() -> List[int]:
    ids = []
    for file in ANKETA_DIR.iterdir():
        if file.suffix == '.json' and file.stem.startswith('anketa_'):
            try:
                ids.append(int(file.stem.split('_')[1]))
            except ValueError:
                continue
    return sorted(ids)

def f_anketa_admin(data: Dict[str, Any]) -> str:
    return (
        f"АНКЕТА №{data['id']}\n"
        f"От пользователя: @{data['username'] or data['user_id']}\n"
        f"--- АНАЛИЗ ---\n"
        f"Статус: {data['status']}\n"
        f"Овнерка: {data['owner_status']}\n"
        f"--- ТЕКСТ ЗАЯВКИ ---\n"
        f"```\n{data['text']}\n```"
    )
    
def f_l_open_anketa(user_id: int) -> Optional[Dict[str, Any]]:
    all_ids = get_a_ids()
    latest_anketa = None
    latest_time = 0
    
    for ank_id in all_ids:
        data = get_anketa(ank_id)
        if data and data['user_id'] == user_id and data['status'] == 'Открыт':
            if data['timestamp'] > latest_time:
                latest_time = data['timestamp']
                latest_anketa = data
                
    return latest_anketa

def p_open_anketa_id(chat_id: int) -> Optional[Dict[str, Any]]:

    all_ids = get_a_ids()
    latest_anketa = None
    latest_time = 0
    
    for ank_id in all_ids:
        data = get_anketa(ank_id)
        if (data and data['status'] == 'Открыт' and 
            data.get('chat_id') == chat_id):
            

            if data['timestamp'] > latest_time:
                latest_time = data['timestamp']
                latest_anketa = data
                
    return latest_anketa


def chat_anketa(user_id: int, chat_id: int) -> Optional[Dict[str, Any]]:

    data = f_l_open_anketa(user_id) 
    
    if data:
        data['chat_id'] = chat_id
        
        file_path = ANKETA_DIR / f"anketa_{data['id']}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return data
        
    return None