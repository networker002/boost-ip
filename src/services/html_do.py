class HTMLdocument:
    def __init__(self, title="Расписание"):
        self.title = title
    default_structure = """
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{title}</title></head><body><style>
*{margin:0;padding:0;box-sizing:border-box} body{font-family:system-ui;background:#fff;color:#111827} header{background:linear-gradient(90deg,#86f386,#9393ff);padding:1rem 2rem;color:#fff;display:flex;justify-content:space-between;align-items:center} #burger{background:#4cf0a3;padding:0.5rem 1rem;border-radius:0.5rem;cursor:pointer;transition:all 0.2s} #burger:hover{background:#fff;color:#4cf0a3} .title-s{text-align:center;background:#e5e7eb;margin:1.5rem;padding:1rem;border-radius:1rem} .schedule{display:grid;grid-template-columns:repeat(6,1fr);gap:1.5rem;padding:1rem} .schedule>div{background:#f3f4f6;padding:1.5rem;border-radius:1rem;box-shadow:0 4px 6px -1px rgba(0,0,0,0.1);display:flex;flex-direction:column} .schedule>div>div{padding:0.5rem 0} .schedule>div>div:last-child{border-bottom:none} .day{background:#dcfce7;color:#166534;font-weight:700;font-size:1.25rem;padding:0.5rem 1rem;border-radius:0.5rem;display:inline-block;margin-bottom:1rem} .time{border-top:1px solid #d1d5db;font-weight:700;color:#374151;font-size:0.875rem;margin-top:0.75rem;padding-top:12px}.schedule > div > div:first-child .time{border-top:none} .subject{font-weight:700;font-size:1.125rem;color:#111827;margin-top:0.25rem} @media(max-width:1450px){.schedule{grid-template-columns:repeat(3,1fr)}} @media(max-width:1110px){.schedule{grid-template-columns:repeat(2,1fr)}} @media(max-width:778px){.schedule{grid-template-columns:1fr}}
</style><header><h3 id="header-title">BoostBot BoostLearn BoostMind</h3><button id="burger" hidden>≡</button></header><div class="title-s"><h1>Расписание занятий</h1></div><div class="schedule">{main}</div></body></html>"""


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
            elif line.startswith("⏰"):
                time = line[2:].strip()
                current_day_lessons.append({"type": "time", "value": time})
            elif line.startswith("📚"):
                subject = line[2:].strip()
                current_day_lessons.append({
                    "type": "subject",
                    "value": subject
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

            html += "</div>"

        html += "</div>"
        return html

    def generate_html(self, data: str) -> str:
        formatted_data = self.format_(data)
        result = self.default_structure.replace("{title}", self.title)
        result = result.replace("{main}", formatted_data)
        return result


#HTMLdocument().generate_html("test")