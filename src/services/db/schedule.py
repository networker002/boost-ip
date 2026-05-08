import json
import logging
import requests as req
from collections import defaultdict
from typing import Dict, List, Any, TypedDict, Optional, Tuple
import os, sys
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from services import get_weeks
from services.db.client import supabase
import random
from pathlib import Path
import asyncio


proxies = {
    "http": os.environ.get('MIET_PROXY'),
    "https": os.environ.get('MIET_PROXY')
}

class Lesson(TypedDict):
    time: str
    time_code: int
    subject: str
    teacher: str
    room: str

logger = logging.getLogger("app")

class Schedule():
    def __init__(self, group_name: str):
        self.group_name = group_name.upper()
        self.ua_path = Path(__file__).parent.parent.parent.parent / "config" / "useragents.txt"
        self.url_path = Path(__file__).parent.parent.parent.parent / "config" / "schedule.json"
        self.timings = Path(__file__).parent.parent.parent.parent / "config" / "example-time.json"

        try:
            with open(self.url_path, encoding="utf-8") as file_schedule:
                data_ = json.load(file_schedule)
                self.url = data_.get("url") + "data?group="
                self.url += self.group_name
        except FileNotFoundError:
            raise FileNotFoundError("Not found!")
        
        try:
            with open(self.ua_path, encoding="utf-8") as f:
                self.data_ua = [line.strip() for line in f if line.strip()]
        except Exception as e: self.data_ua = []
    def get_Time(self) -> dict | tuple:
        try:
            with open(self.timings, "r", encoding="utf-8") as f:
                d = json.load(f)
                
            return d
            try:
                ua = random.choice(self.data_ua)
                headers={"User-Agent":ua}
            except Exception: headers = None
            resp = req.get(url=self.url + "'", headers=headers, proxies=(proxies if os.environ.get("MIET_PROXY") else None))
            if resp.status_code == 200:
                Data = resp.json()
                return Data  # {Times:...}
            else: 
                print(f"Failed to fetch schedule data. Status code: {resp.status_code}")
                return None
        except Exception as e:
            print(e)
            return None
        
    def set_Time(self) -> list:
        schedule = self.get_Time()
        if schedule:
            schedule: list = schedule.get("Times", [])
            return schedule
        return []

    def parse_by_group(self, get_old:bool = False):

        res = supabase.table("schedule_updates").select("*").eq("group_name", self.group_name).execute()
        if res.data:
            data = res.data[0]
            ct = data.get('content', {})
            ctd = ct.get("Data", [])
            if get_old:
                ct_old = data.get("old_content", {}) or {}
                ctd_old = ct_old.get("Data", [])
                return ctd, ctd_old
            return ctd
        else:
            print("No data for group:", self.group_name)
            return ([], []) if get_old else []

    async def get_schedule_async(self, prev_next:bool = False) -> Tuple[str, Dict[str, Any]] | Tuple[Tuple[str, Dict[str, Any]], Tuple[str, Dict[str, Any]], Tuple[str, Dict[str, Any]]]:
        timings, subjects_and_old = await asyncio.to_thread(
            lambda: (self.set_Time(), self.parse_by_group(get_old=True))
        )
        
        if len(subjects_and_old) == 2:
            subjects, old_subjects = subjects_and_old
        else:
            subjects, old_subjects = subjects_and_old, []

        # print("t", timings)
        # print("s", subjects)
        
        if not timings or not subjects:
            print("No schedule data available.")
            return {}

        days = defaultdict(lambda: defaultdict(list))
        old_days = defaultdict(lambda: defaultdict(list))
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
            subgroup = div_days.get(int(lesson["DayNumber"]))
            time_info = lesson["Time"]
            time_idx = time_info["Code"]
            time_name = timings[int(time_idx)]["Time"] if 0 <= int(time_idx) < len(timings) else "0 пара"

            lesson_data = {
                    'time': time_name,
                    'time_code': time_idx,
                    'subject': lesson["Class"]["Name"],
                    'teacher': lesson["Class"]["TeacherFull"],
                    'room': lesson["Room"]["Name"] or "Не указана"
                }

            days[day][subgroup].append(lesson_data)


        for lesson in old_subjects:
            day = lesson["Day"]
            subgroup = div_days.get(int(lesson["DayNumber"]))
            time_info = lesson["Time"]
            time_idx = time_info["Code"]
            time_name = timings[int(time_idx)]["Time"] if 0 <= int(time_idx) < len(timings) else "0 пара"

            lesson_data = {
                    'time': time_name,
                    'time_code': time_idx,
                    'subject': lesson["Class"]["Name"],
                    'teacher': lesson["Class"]["TeacherFull"],
                    'room': lesson["Room"]["Name"] or "Не указана"
                }

            old_days[day][subgroup].append(lesson_data)
        result = {}
        result2 = {}
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

        for day_num in sorted(old_days.keys()):
            day_schedule = {}
            for subgroup in sorted(old_days[day_num].keys()):
                day_schedule[subgroup] = sorted(
                    old_days[day_num][subgroup], 
                    key=lambda x: x['time_code']
                )
            result2[day_num] = {
                'name': day_names.get(day_num, f'День {day_num}'),
                'divided': day_schedule
            }

        # print("RES1: ", result)
        # print("RES: ",result2)
        return get_weeks.group_now_week(result) if not prev_next else ( get_weeks.group_now_week(result2, week_type=get_weeks.prev), get_weeks.group_now_week(result), get_weeks.group_now_week(result, week_type=get_weeks.next) )

    def get_two_weeks(self):
        timings = self.set_Time()
        subjects, old_subjects = self.parse_by_group(get_old=True)

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
            time_idx = time_info["Code"]
            time_name = timings[time_idx]["Time"] if 0 <= time_idx < len(timings) else "0 пара"

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

        return get_weeks.group_now_week(result, previos=True)


    def run_(self, prev_next:bool = False) -> Tuple[str, Dict] | Any:
        timings = self.set_Time()
        subjects, old_subjects = self.parse_by_group(get_old=True)

        if not timings or not subjects:
            print("No schedule data available.")
            return {}

        days = defaultdict(lambda: defaultdict(list))
        old_days = defaultdict(lambda: defaultdict(list))
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
            subgroup = div_days.get(int(lesson["DayNumber"]))
            time_info = lesson["Time"]
            time_idx = time_info["Code"]
            time_name = timings[int(time_idx)]["Time"] if 0 <= int(time_idx) < len(timings) else "0 пара"

            lesson_data = {
                    'time': time_name,
                    'time_code': time_idx,
                    'subject': lesson["Class"]["Name"],
                    'teacher': lesson["Class"]["TeacherFull"],
                    'room': lesson["Room"]["Name"] or "Не указана"
                }

            days[day][subgroup].append(lesson_data)


        for lesson in old_subjects:
            day = lesson["Day"]
            subgroup = div_days.get(int(lesson["DayNumber"]))
            time_info = lesson["Time"]
            time_idx = time_info["Code"]
            time_name = timings[int(time_idx)]["Time"] if 0 <= int(time_idx) < len(timings) else "0 пара"

            lesson_data = {
                    'time': time_name,
                    'time_code': time_idx,
                    'subject': lesson["Class"]["Name"],
                    'teacher': lesson["Class"]["TeacherFull"],
                    'room': lesson["Room"]["Name"] or "Не указана"
                }

            old_days[day][subgroup].append(lesson_data)
        print("OLD",old_days)
        result = {}
        result2 = {}
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

        for day_num in sorted(old_days.keys()):
            day_schedule = {}
            for subgroup in sorted(old_days[day_num].keys()):
                day_schedule[subgroup] = sorted(
                    old_days[day_num][subgroup], 
                    key=lambda x: x['time_code']
                )
            result2[day_num] = {
                'name': day_names.get(day_num, f'День {day_num}'),
                'divided': day_schedule
            }


        #print("RES: ",result2)
        return get_weeks.group_now_week(result) if not prev_next else ( get_weeks.group_now_week(result2, week_type=get_weeks.prev), get_weeks.group_now_week(result), get_weeks.group_now_week(result, week_type=get_weeks.next) )
