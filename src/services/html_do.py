class HTMLdocument:
    def __init__(self, title="Расписание"):
        self.title = title
    default_structure = """<!DOCTYPE html> <html lang="en"> <head> <meta charset="UTF-8"> <meta name="viewport" content="width=device-width, initial-scale=1.0"> <title>Расписание</title> </head> <body> <style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:system-ui;background:#fff;color:#111827}header{background:linear-gradient(90deg,#86f386,#9393ff);padding:.5rem 1rem;color:#fff;display:flex;flex-direction:column;justify-content:space-between;align-items:center}#burger{background:#4cf0a3;padding:.5rem 1rem;border-radius:.5rem;cursor:pointer;transition:all .2s}#burger:hover{background:#fff;color:#4cf0a3}.title-s{text-align:center;background:#ffeaff3a;box-shadow:insert 2px 2px 2em #0000003a;margin:1.5rem;padding:1rem;border-radius:1rem}.schedule{display:grid;grid-template-columns:repeat(6,1fr);gap:1.5rem;padding:1rem}.schedule>div{background:#f3f4f6;padding:1.5rem;border-radius:1rem;box-shadow:0 4px 6px -1px rgba(0,0,0,.1);display:flex;flex-direction:column}.schedule>div>div{padding:.5rem 0}.schedule>div>div:last-child{border-bottom:none}.day{background:#dcfce7;color:#166534;font-weight:700;font-size:1.25rem;padding:.5rem 1rem;border-radius:.5rem;display:inline-block;margin-bottom:1rem}.now{background:#aaffb5;box-shadow:0 0 1em #aaffb5}.time{border-top:1px solid #d1d5db;font-weight:700;color:#374151;font-size:.875rem;margin-top:.75rem;padding-top:12px}.schedule>div>div:first-child .time{border-top:none}.subject{font-weight:700;font-size:1.125rem;color:#111827;margin-top:.25rem}.room{color:#707172}@media(max-width:1450px){.schedule{grid-template-columns:repeat(3,1fr)}}@media(max-width:1110px){.schedule{grid-template-columns:repeat(2,1fr)}}@media(max-width:778px){.schedule{grid-template-columns:1fr}}</style> <header> <div class="title-s"> <h1>Расписание занятий</h1> </div> <h5 id="nowDateFull"></h5> </header> <div class="schedule">{main}</div><script>var d=new Date(),n=d.getDay(),m=d.getMonth(),dt=d.getDate(),days={1:"Понедельник",2:"Вторник",3:"Среда",4:"Четверг",5:"Пятница",6:"Суббота",7:"Воскресенье"},months={0:"января",1:"февраля",2:"марта",3:"апреля",4:"мая",5:"июня",6:"июля",7:"августа",8:"сентября",9:"октября",10:"ноября",11:"декабря"},dayCall=days[n]??"Воскресенье",full=dayCall+", "+dt+" "+(months[m]??0);document.getElementById("nowDateFull").innerHTML=full;document.querySelectorAll(".day").forEach(el=>{if(el.innerHTML===dayCall)el.classList.add("now")});</script></body></html>"""


    @staticmethod
    def format_(data: str) -> str:
        lines = [line.strip() for line in data.split("\n") if line.strip()]
        schedule_html = ""
        current_day_lessons = []
        current_day = None

        for line in lines:
            if line.startswith("📅"):
                if current_day:
                    schedule_html += HTMLdocument._render_day_group(current_day, current_day_lessons)

                current_day = line[2:].strip()
                current_day_lessons = []
            elif line[1:].strip().startswith("пара"):
                time = line[:].strip()
                current_day_lessons.append({"type": "time", "value": time})
            elif line.startswith("—"):pass
            else:
                if not line[-6:].endswith("ана)"):
                    subject = line[:-6].strip() 
                    room = line[-6:] 
                else:
                    subject = line[:-12].strip()
                    room = "(Не указана)"
         
                current_day_lessons.append({
                    "type": "subject",
                    "value": subject
                })
                current_day_lessons.append({
                    "type": "room",
                    "value": "Ауд. "+room[1:-1]
                })



        if current_day:
            schedule_html += HTMLdocument._render_day_group(current_day, current_day_lessons)

        return schedule_html

    @staticmethod
    def _render_day_group(day_name: str, lessons: list) -> str:
        html = "<div>"
        is_first_lesson = True

        for lesson in lessons:
            html += "<div>"

            if is_first_lesson and lesson["type"] == "time":
                html += f'<p class="day">{day_name}</p>'
                is_first_lesson = False

            if lesson["type"] == "time":
                html += f'<p class="time">{lesson["value"]}</p>'
            elif lesson["type"] == "subject":
                html += (
                    f'<p class="subject">{lesson["value"]}</p>'
                )
            elif lesson["type"] == "room":
                html += (
                    f'<p class="room">{lesson["value"]}</p>'
                )

            html += "</div>"

        html += "</div>"
        return html

    def generate_html(self, data: str) -> str:
        formatted_data = self.format_(data)
        result = self.default_structure.replace("{title}", self.title)
        result = result.replace("{main}", formatted_data)
        return result

test = """Вот твое расписание
(2 знаменатель)

——————————————
📅 Понедельник

0 пара 08:30 - 08:50
Разговоры о важном (3216)

1 пара 09:00 - 10:20
История (8102)

2 пара 10:30 - 11:50
Информатика (8231)

2 пара 10:30 - 11:50
Информатика (8208)

——————————————
📅 Вторник

1 пара 09:00 - 10:20
Математика (8102)

2 пара 10:30 - 11:50
Физика (8109)

3 пара 12:00 - 13:20
Литература (8111)

4 пара 14:00 - 15:20
Физическая культура (Не указана)

——————————————
📅 Среда

2 пара 10:30 - 11:50
Введение в специальность (3216)

3 пара 12:00 - 13:20
Математика (8102)

4 пара 14:00 - 15:20
История (1202)

5 пара 15:30 - 16:50
Основы безопасности и защиты Родины (1203)

——————————————
📅 Четверг

1 пара 09:00 - 10:20
Математика (8102)

2 пара 10:30 - 11:50
Физика (8109)

——————————————
📅 Пятница

2 пара 10:30 - 11:50
Математика (8102)"""

# print(HTMLdocument().generate_html(test))