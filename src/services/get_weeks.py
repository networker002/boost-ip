import datetime
from zoneinfo import ZoneInfo
from typing import *

try:
    tz = ZoneInfo("Europe/Moscow")
    now = datetime.datetime.now(tz=tz)
    start = datetime.datetime(2026, 4, 30, tzinfo=tz)
except Exception as e:
    print(f"TZ Error: {e}")
    tz = None
    now = datetime.timedelta. datetime.datetime.now()
    start = datetime.datetime(now.year, 4, 30)

mapping = {
    0: "1 числитель",
    1: "1 знаменатель",
    2: "2 числитель",
    3: "2 знаменатель"
}

week_passed = (now - start).days // 7

days_name = {1:"Понедельник", 2:"Вторник", 3:"Среда", 4:"Четверг", 5:"Пятница", 6:"Суббота"}

def group_now_week(data: Dict[int, Dict[int, List[Dict[str, Any]]]]) -> Tuple[str, Dict]:
    now_is = mapping.get(week_passed % 4, "Неизвестная неделя")
    
    response = {"Понедельник": [], "Вторник": [], "Среда": [], "Четверг": [], "Пятница": [], "Суббота": []}
    
    for i in range(1, 7):
        try:
            if now_is in data[i]["divided"]:
                response[days_name.get(i)].append(data[i]["divided"][now_is])
        except (KeyError, TypeError):
            pass
    
    return now_is or "Неизвестная неделя", response

print(mapping.get(week_passed % 4, "Неизвестная неделя"))