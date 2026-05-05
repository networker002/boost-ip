import json
import requests as req
from collections import defaultdict
from typing import Dict, List, Any, TypedDict, Optional, Tuple
# import os, sys
# from pathlib import Path
# sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from services import get_weeks
from services.db.client import supabase
import random
from pathlib import Path
import asyncio
from ...main import logger

class Lesson(TypedDict):
    time: str
    time_code: int
    subject: str
    teacher: str
    room: str
     

class Schedule():
    def __init__(self, group_name: str):
        self.group_name = group_name.upper()
        self.ua_path = Path(__file__).parent.parent.parent.parent / "config" / "useragents.txt"
        self.url_path = Path(__file__).parent.parent.parent.parent / "config" / "schedule.json"

        try:
            with open(self.url_path, encoding="utf-8") as file_schedule:
                data_ = json.load(file_schedule)
                self.url = data_.get("url") + "data?group="
        except FileNotFoundError:
            raise FileNotFoundError("Not found!")
        
        try:
            with open(self.ua_path, encoding="utf-8") as f:
                self.data_ua = [line.strip() for line in f if line.strip()]
        except Exception as e: self.data_ua = []
    def get_Time(self) -> dict | tuple:
        try:
            try:
                ua = random.choice(self.data_ua)
                headers={"User-Agent":ua}
            except Exception: headers = None
            resp = req.get(url=self.url + "'", headers=headers)
            if resp.status_code == 200:
                Data = resp.json()
                return Data  # {Times:...}
            else: 
                return ("Not found", 404)
        except Exception as e:
            return (None, "Error " + str(e))
        
    def set_Time(self) -> list:
        schedule = self.get_Time()
        if not str(schedule).startswith("(No") and not str(schedule).startswith("(Error") or isinstance(schedule, dict):
            schedule: list = schedule.get("Times", [])
            return schedule
        return []

    def parse_by_group(self) -> List[Dict[str, Any]]:
        self.url += self.group_name.upper()

        res = supabase.table("schedule_updates").select("*").eq("group_name", self.group_name).execute()

        if res.data:
            logger.info(f"Have data, {len(res.data)} elements")
            data = res.data[0]
            ct = data['content']
            logger.info(ct)
            ctd = ct["Data"]
            logger.info(ctd)
            return ctd

    async def get_schedule_async(self) -> Tuple[str, Dict[str, Any]]:
        timings, subjects = await asyncio.to_thread(
            lambda: (self.set_Time(), self.parse_by_group())
        )
        
        if not timings or not subjects:
            return {}, {}

        days = defaultdict(lambda: defaultdict(list))
        day_names = {
            1: 'Понедельник', 
            2: 'Вторник', 
            3: 'Среда', 
            4: 'Четверг',
            5: 'Пятница'
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
            time_name = timings[time_idx - 1]["Time"] if 0 < time_idx <= len(timings) else "0 пара"
            
            lesson_data = {
                'time': time_name,
                'time_code': time_idx,
                'subject': lesson["Class"]["Name"],
                'teacher': lesson["Class"]["Teacher"],
                'room': lesson["Room"]["Name"] or "Не указана"
            }
            # print(lesson_data)
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

        
        return get_weeks.group_now_week(result)
    
    def get_two_weeks(self):
        timings = self.set_Time()
        subjects = self.parse_by_group()
        # print(147)
        # print(subjects)

        if not timings or not subjects:
            return {}, {}, {}, {}

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
            time_name = timings[time_idx - 1]["Time"] if 0 < time_idx <= len(timings) else "0 пара"
            
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

        return get_weeks.group_now_week(result, previos=True)


    def run_(self) -> Tuple[str, Dict] | Any:
        timings = self.set_Time()
        subjects = self.parse_by_group()
    
        # print("!")
        # print(timings)
        # print(subjects)
        if not timings or not subjects:
            print("No schedule data available.")
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
            subgroup = div_days.get(int(lesson["DayNumber"]))
            time_info = lesson["Time"]
            time_idx = time_info["Code"]
            print(lesson)
            time_name = timings[int(time_idx) - 1]["Time"] if 0 < int(time_idx) <= len(timings) else "0 пара"
            
            lesson_data = {
                'time': time_name,
                'time_code': time_idx,
                'subject': lesson["Class"]["Name"],
                'teacher': lesson["Class"]["TeacherFull"],
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
    
# print(Schedule("ИС-25-14О").run_())
