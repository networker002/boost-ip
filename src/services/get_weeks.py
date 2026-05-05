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

def group_now_week(data: Dict[int, Dict[int, List[Dict[str, Any]]]], previos: bool = False) -> Tuple[str, Dict]:
    now_is = mapping.get(week_passed % 4, "Неизвестная неделя")
    previos_week = mapping.get((week_passed - 1) % 4, "Неизвестная неделя")
    
    response = {"Понедельник": [], "Вторник": [], "Среда": [], "Четверг": [], "Пятница": [], "Суббота": []}
    
    
    if previos == False:
        
        # if previos:
        #     response = [[{"Понедельник": []}, {"Вторник": []}, {"Среда": []}, {"Четверг": []}, {"Пятница": []}, {"Суббота": []}], [{"Понедельник": []}, {"Вторник": []}, {"Среда": []}, {"Четверг": []}, {"Пятница": []}, {"Суббота": []}]]
         
        for i in range(1, 7):
            try:
                if now_is in data[i]["divided"]:
                    response[days_name.get(i)].append(data[i]["divided"][now_is])
                    # if previos:
                    #     response[days_name.get(i)].append(data[i]["divided"][previos_week])
            except (KeyError, TypeError):
                pass
            
    else:
        for i in range(1, 7):
            try:
                if now_is in data[i]["divided"]:
                    response[days_name.get(i)].append(data[i]["divided"][now_is])
                    response[days_name.get(i)].append(data[i]["divided"][previos_week])
                    # if previos:
                    #     response[days_name.get(i)].append(data[i]["divided"][previos_week])
            except (KeyError, TypeError):
                pass
            
            
    return now_is or "Неизвестная неделя", response
        
    # elif previos:
    #     previos_response = response[0]
    #     now_response = response[1]
    #     now_data = {}
    #     previos_data = {}
        

    #     for i in previos_response:
    #         try:
    #             if now_is in data[i]["divided"]:
    #                 previos_data[days_name.get(i)] = data[i]["divided"][previos_week]
    #         except (KeyError, TypeError):
    #             pass
            
    # for i in now_response:
    #     try:
    #             if now_is in data[i]["divided"]:
    #                 now_data[days_name.get(i)] = data[i]["divided"][now_is]
    #         except (KeyError, TypeError):
    #             pass
            
    #     return now_is or "Неизвестная неделя", now_data, previos_week or "Неизвестная неделя", previos_data
        


print(mapping.get(week_passed % 4, "Неизвестная неделя"))