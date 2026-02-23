import datetime
from zoneinfo import ZoneInfo
from typing import *

now = datetime.datetime.now(tz=ZoneInfo("Europe/Moscow"))
now_full = (now.day, now.month)

start = datetime.datetime(now.year, 1, 5, tzinfo=ZoneInfo("Europe/Moscow"))


weekday_now = datetime.date(now.year, now.month, now.day).weekday()

week_passed = (now - start).days // 7

mapping = {
    0: "1 числитель",
    1: "1 знаменатель",
    2: "2 числитель",
    3: "2 знаменатель"
}

days_name = {1:"Понедельник", 2:"Вторник", 3:"Среда", 4:"Четверг", 5:"Пятница", 6:"Суббота"}

def group_now_week(data: Dict[int, Dict[int, List[Dict[str, Any]]]]) -> Tuple[str, Dict]:
    response = {
        "Понедельник": [],
        "Вторник": [], 
        "Среда": [], 
        "Четверг": [],
        "Пятница": [],
        "Суббота": []
    }
    now_is = mapping.get(week_passed%4)

    days =  data

    for i in range(1, 7):
        try:
            response[days_name.get(i)].append(days[i]["divided"][now_is])
        except KeyError:
            pass


    return now_is, response
