import datetime
from zoneinfo import ZoneInfo
from typing import *

try:
    tz = ZoneInfo("Europe/Moscow")
    now = datetime.datetime.now(tz=tz)
    start = datetime.datetime(2026, 3, 29, tzinfo=tz)
except Exception as e:
    print(f"TZ Error: {e}")
    tz = None
    now = datetime.datetime.now()
    start = datetime.datetime(now.year, 3, 29)

mapping = {
    0: "1 числитель",
    1: "1 знаменатель",
    2: "2 числитель",
    3: "2 знаменатель"
}

week_passed = (now - start).days // 7

days_name = {1:"Понедельник", 2:"Вторник", 3:"Среда", 4:"Четверг", 5:"Пятница", 6:"Суббота"}
now_is = mapping.get(week_passed % 4, "Неизвестная неделя")
prev = mapping.get((week_passed - 1) % 4, "Неизвестная неделя")
next = mapping.get((week_passed + 1) % 4, "Неизвестная неделя")

def group_now_week(data: Dict[int, Dict[str, Any]], week_type: Optional[str] = None) -> Tuple[str, Dict[str, List[Dict[str, Any]]]]:
    if week_type is None:
        week_type = now_is
    
    response = {"Понедельник": [], "Вторник": [], "Среда": [], "Четверг": [], "Пятница": [], "Суббота": []}
    
    for i in range(1, 7):
        day_name = days_name.get(i)
        if day_name and week_type in data.get(i, {}).get("divided", {}):
            response[day_name] = data[i]["divided"][week_type]
    
    return week_type, response
        
print(mapping.get(week_passed % 4, "Неизвестная неделя"))