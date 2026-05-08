import os, sys
import httpx
import json
import datetime
import asyncio
from pathlib import Path
import random
from aiogram import Bot, Dispatcher
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, WebAppInfo


ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from services.db.client import supabase

CONFIG_DIR = ROOT_DIR / "config"
SCHEDULE_JSON = CONFIG_DIR / "schedule.json"
GROUPS_JSON = CONFIG_DIR / "groups.json"
UA = CONFIG_DIR / "useragents.txt"

MIET_PROXY = os.environ.get("MIET_PROXY")
BOT = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))

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

time_start = datetime.datetime.now()

try:
    with open(UA, "r", encoding="utf-8") as f:
        user_agents = [line.strip() for line in f.readlines() if line.strip()]
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Critical error: {e}")
    sys.exit(1)

try:
    with open(SCHEDULE_JSON, "r", encoding="utf-8") as f:
        config_data = json.load(f)
        url_gr = config_data.get("url")
        url_grs = url_gr + "groups"
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Critical error: {e}")
    sys.exit(1)

async def check_groups():
    print("Checking groups...")
    data = {}


    if GROUPS_JSON.exists():
        try:
            with open(GROUPS_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            pass

    created_at_str = data.get("created_at")
    groups = data.get("groups", [])


    is_fresh = False
    if created_at_str and groups:
        created_at_dt = datetime.datetime.fromisoformat(created_at_str)
        if (datetime.datetime.now() - created_at_dt).days < 7:
            is_fresh = True

    if is_fresh:
        print("Groups data is fresh.")
        return groups, created_at_str
    else:
        print("Groups data is outdated or missing, fetching new data...")
        async with httpx.AsyncClient(verify=False, timeout=15.0, ) as client:
            
            response = await client.get(url_grs, headers={"User-Agent": random.choice(user_agents)})
        if response.status_code == 200:
            groups = response.json()
            new_created_at = datetime.datetime.now().isoformat()
            print(f"Successfully fetch groups: {groups}")

            with open(GROUPS_JSON, "w", encoding="utf-8") as f:
                json.dump({"created_at": new_created_at, "groups": groups}, f, ensure_ascii=False, indent=4)
            return groups, new_created_at
        else:
            print(f"Failed to fetch groups: {response.status_code}")
            return groups, created_at_str

async def update_schedule():
    groups, created_at_str = await check_groups()
    if not groups:
        return

    for group in groups:
        ua =  random.choice(user_agents)
        print(f"[{datetime.datetime.now().hour}:{datetime.datetime.now().minute}:{datetime.datetime.now().second}] Updating schedule for group: {group}\n User-Agent: {ua}")
        url_group = f"{url_gr}data?group={group}"
        async with httpx.AsyncClient(verify=False, timeout=15.0, ) as client:

            response = await client.get(url_group, headers={"User-Agent": ua})

        if response.status_code == 200:
            schedule_json = response.json()
            # print(schedule_json)

            #print(f"Successfully fetch schedule: {schedule_json}")
            existing_record = supabase.table("schedule_updates").select("*").eq("group_name", group).execute()

            if existing_record.data:
                #print(f"[{datetime.datetime.now().hour}:{datetime.datetime.now().minute}:{datetime.datetime.now().second}] Updating existing record for group: {group}")
                last_upd = existing_record.data[0].get("last_checked")
                
                if (datetime.datetime.now() - datetime.datetime.fromisoformat(last_upd)).days > 7:
                    #print(f"Schedule for {group} was updated recently at {last_upd}")
                    old_data = supabase.table("schedule_updates").select("old_content").eq("group_name", group).execute()
                    
                    # mapping = {
                    #     0: "1 числитель",
                    #     1: "1 знаменатель",
                    #     2: "2 числитель",
                    #     3: "2 знаменатель"
                    # }

                    mp = {
                    0: 3,
                    1: 0,
                    2: 1,
                    3: 2
                    }
                    
                    old_ct = None

                    week_passed = (now - start).days // 7
                    #print(schedule_json.get("Data", []))
                    for day in schedule_json["Data"]:
                        if day["DayNumber"] == mp.get(week_passed%4):
                            old_ct = day
                    if old_data.data and old_data.data[0].get("old_content") != schedule_json:
                        #print(f"Old content for {group} has changed.")
                        supabase.table("schedule_updates").update({"old_content": old_ct, "last_checked": datetime.datetime.now().isoformat(),}).eq("group_name", group).execute()
                        print(f"Old content for {group} updated in DB.")
                    elif not old_data.data:
                        supabase.table("schedule_updates").insert({"old_content": old_ct, "last_checked": datetime.datetime.now().isoformat(),}).eq("group_name", group).execute()
                        print(f"Old content for {group} inserted into DB.")

                if existing_record.data[0].get("content") != schedule_json:
                    builder = InlineKeyboardBuilder()
                    builder.row(InlineKeyboardButton(
                        text="Проверить", 
                        web_app=WebAppInfo(url="https://networker002.github.io/webapp/")
                    ))

                    print(f"Schedule for {group} has changed, updating DB.")
                    msg = "<b>🔔 Расписание поменялось!</b> Проверьте обновленное расписание"
                    users = supabase.table("user_groups").select("tg_id", "group_name").eq("group_name", group).execute()
                    for user in users.data:
                        user_id = user.get("tg_id")
                        await BOT.send_message(chat_id=user_id, text=msg, parse_mode="HTML", reply_markup=builder.as_markup())
                        asyncio.sleep(0.1)

                supabase.table("schedule_updates").update({
                    # "last_checked": datetime.datetime.now().isoformat(), 
                    "content": schedule_json
                }).eq("group_name", group).execute()
                print(f"Schedule for {group} updated in DB.")
            else:
                print(f"[{datetime.datetime.now().hour}:{datetime.datetime.now().minute}:{datetime.datetime.now().second}] Inserting new record for group: {group}")
                supabase.table("schedule_updates").insert({
                    "group_name": group, 
                    # "last_checked": datetime.datetime.now().isoformat(), 
                    "content": schedule_json
                }).execute()
                print(f"Schedule for {group} inserted into DB.")
        else:
            print(f"Failed to fetch schedule for {group}: {response.status_code}")

    print(f"Schedule update completed in {(datetime.datetime.now() - time_start).total_seconds()} seconds.")

if __name__ == "__main__":
    asyncio.run(update_schedule())
