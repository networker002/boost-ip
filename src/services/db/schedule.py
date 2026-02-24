import json
import requests as req
from collections import defaultdict
from typing import Dict, List, Any, TypedDict, Optional, Tuple
from services import get_weeks
import random

class Lesson(TypedDict):
    time: str
    time_code: int
    subject: str
    teacher: str
    room: str
     

class Schedule():
    def __init__(self, group_name: str, url: Optional[str] = None):
        self.group_name = group_name.upper()
        self.url = url

        try:
            with open("config/schedule.json", "r") as file_schedule:
                data_ = json.load(file_schedule)
                self.url = data_.get("url") + "data?group="
        except FileNotFoundError: 
            raise FileNotFoundError("Not found!")
        
        try:
            with open("config/useragents.txt", "r") as f:
                data__ = f.read()
                self.useragents = data__.split("\n")
        except Exception as e: print(e)
    def get_Time(self) -> dict | tuple:
        try:
            test_url = self.url + "'"
            ua = random.choice(self.useragents)
            resp = req.get(url=test_url, headers={"User-Agent": ua})
            if resp.status_code == 200:
                Data = resp.json()
                return Data  # {Times:...}
            else: 
                return ("Not found", 404)
        except Exception as e:
            return (None, "Error " + str(e))
        
    def set_Time(self) -> list:
        schedule = self.get_Time()
        if not str(schedule).startswith("(No"):
            schedule: list = schedule.get("Times")
            return schedule

    def parse_by_group(self) -> List[Dict[str, Any]]:
        # url_example = "https://www.miet.ru/schedule/data?group=%D0%98%D0%A1-25-14%D0%9E"
        self.url += self.group_name.upper()

        res = req.get(url=self.url)
        
        if res.status_code == 200:
            data: list = res.json()["Data"]
            return data
        return []   


    def run_(self) -> Tuple[str, Dict] | Any:

        timings = self.set_Time()
        subjects = self.parse_by_group()
    
        if not timings or not subjects:
            return {}

        days = defaultdict(lambda: defaultdict(list))
        day_names = {
            1: 'Понедельник', 
            2: 'Вторник', 
            3: 'Среда', 
            4: 'Четверг',
            5: 'Пятницa'
        }
        div_days = {
            0: "1 числитель",
            1: "1 знаменатель",
            2: "2 числитель",
            3: "2 знаменатель"
        }

        for lesson in subjects:
            day = lesson["Day"]
            subgroup = div_days.get(lesson["DayNumber"])
            time_info = lesson["Time"]
            time_idx = time_info["Time"]
            time_name = timings[time_idx - 1]["Time"] if 0 < time_idx < len(timings) + 1 else "0 пара"
            
            lesson_data = {
                'time': time_name,
                'time_code': time_idx,
                'subject': lesson["Class"]["Name"],
                'teacher': lesson["Class"]["Teacher"],
                'room': lesson["Room"]["Name"] or "Не указана"
            }
            
            days[day][subgroup].append(lesson_data)

        
        result = {}
        for day_num in sorted(days.keys()):
            day_schedule = {}
            for subgroup in sorted(days[day_num].keys()):
                day_schedule[subgroup] = sorted(
                    days[day_num][subgroup], 
                    key=lambda x: x['time_code']
                )
            result[day_num] = {
                'name': day_names.get(day_num, f'День {day_num}'),
                'divided': day_schedule
            }
        # 0 -- 1 числитель
        # 1 -- 1 знаменатель
        # 2 -- 2 числитель
        # 3 -- 2 знаменатель

        #result[week_day][[day_name]|[data[0|1|2|3]]]

        return get_weeks.group_now_week(result)
