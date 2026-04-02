import requests
import json
import datetime
from pathlib import Path
import random

def groups_req() -> None:
    url = "https://www.miet.ru/schedule/groups"
    try:
        with open(Path(__file__).parent.parent.parent / "config" / "useragents.txt", encoding="utf-8") as f:
            user_agents = [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        user_agents = ["Mozilla/5.0"]
    
    headers = {
        "User-Agent": random.choice(user_agents) if user_agents else "Mozilla/5.0"
    }

    try:
        res = requests.get(url=url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            create_time = datetime.datetime.now().isoformat()
            json_data = {
                "created_at": create_time,
                "groups": data
            }
            with open(Path(__file__).parent.parent.parent / "config" / "groups.json", "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error fetching groups: {e}")


def get_groups() -> list:
    groups_path = Path(__file__).parent.parent.parent / "config" / "groups.json"
    try:
        if not groups_path.exists():
            print("Groups file not found. Fetching...")
            groups_req()
            
        with open(groups_path, encoding="utf-8") as f:
            data = json.load(f)
            
            if data.get("created_at"):
                created_at = datetime.datetime.fromisoformat(data["created_at"])
                if (datetime.datetime.now() - created_at).total_seconds() > 24 * 3600:
                    print("Groups data is outdated. Fetching new data...")
                    groups_req()
                    return get_groups()
                else:
                    return data.get("groups", [])
            else:
                print("Groups data is missing creation time. Fetching new data...")
                groups_req()
                return get_groups()
            
    except FileNotFoundError:
        print("Groups file not found. Fetching groups...")
        groups_req()
        return get_groups()
    
    except (json.JSONDecodeError, FileNotFoundError, KeyError):
        print("Groups file is empty or corrupted. Re-fetching...")
        groups_req()
        
        try:
            with open(groups_path, encoding="utf-8") as f:
                data = json.load(f)
                return data.get("groups", [])
        except Exception as e:
            print(f"Final attempt failed: {e}")
            return []