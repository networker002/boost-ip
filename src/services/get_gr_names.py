import requests
import json
import datetime
from pathlib import Path


async def groups_req() -> None:
    url = "https://www.miet.ru/schedule/groups"
    try:
        res = await requests.get(url=url)
        if res.status_code == 200:
            data = res.json()
            create_time = datetime.datetime.now().isoformat()
            json_data = {
                "created_at": create_time,
                "groups": data
            }
            with open(Path(__file__).parent.parent / "config" / "groups.json", "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error fetching groups: {e}")


async def get_groups() -> list:
    groups_path = Path(__file__).parent.parent / "config" / "groups.json"
    try:
        with open(groups_path, encoding="utf-8") as f:
            data = json.load(f)
            if data.get("created_at"):
                created_at = datetime.datetime.fromisoformat(data["created_at"])
                if (datetime.datetime.now() - created_at).total_seconds() > 24 * 3600:
                    print("Groups data is outdated. Fetching new data...")
                    await groups_req()
                    return await get_groups()
                else:
                    return data.get("groups", [])
            else:
                print("Groups data is missing creation time. Fetching new data...")
                await groups_req()
                return await get_groups()
            
    except FileNotFoundError:
        print("Groups file not found. Fetching groups...")
        await groups_req()
        return await get_groups()