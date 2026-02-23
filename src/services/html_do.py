class HTMLdocument:
    def __init__(self, title="Расписание"):
        self.title = title
    default_structure = """
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{title}</title></head><body><style>*{ padding:0;margin:0} :root{--bg:#fff;--txt:#000} body{box-sizing:border-box} header{background:linear-gradient(90deg,rgb(135,248,135),rgb(147,147,255));padding:.75em 2rem;font-size:large;font-family:system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Oxygen,Ubuntu,Cantarell,'Open Sans','Helvetica Neue',sans-serif;color:var(--bg);font-weight:700;letter-spacing:1px;display:flex;justify-content:space-between;flex-wrap:wrap} #burger{background:#4cf0a3;border:0;position:relative;scale:1.5;background:#4cf0a3;min-width:40px;border-radius:10px;transition:all 1s ease,transform .2s;font-size:larger;filter:drop-shadow(4px 6px 4px #00000083)} #burger:hover{background-color:#fff;filter:drop-shadow(5px 7px 6px #000000e0)} #burger:active{transform:translateY(5px)} .title-s{text-align:center;margin:1em 5em;border-radius:16px;padding:.2em;font-family:'Lucida Sans','Lucida Sans Regular','Lucida Grande','Lucida Sans Unicode',Geneva,Verdana,sans-serif;background:rgb(214,214,214);box-shadow:4px 4px 6px rgba(0,0,0,0.3)} .schedule{display:grid;grid-template-columns:repeat(6,1fr);gap:10px} .schedule > div{background:rgb(233,232,232);margin:1em 3em;padding:12px;border-radius:8px;box-shadow:4px 4px 12px rgba(0,0,0,0.25)} .schedule > div div{border-bottom:0 solid rgb(168,167,167);margin-top:6px;margin-bottom:6px} .schedule > div div:last-child{border-bottom:none} .subject{border-bottom:1px solid} p{white-space:nowrap;font-family:system-ui} .day{padding-top:4px;padding-bottom:6px;font-size:x-large;font-weight:700;color:#288a5c;background:#c2ebd7c7;padding-left:6px;border-radius:12px} .time{font-weight:700;color:rgb(71,71,71);letter-spacing:1px;padding-top:10px} .subject{font-weight:700;font-size:larger;padding-top:6px;padding-bottom:10px} .classroom{font-family:monospace;letter-spacing:1.5px;color:rgb(107,107,107);font-size:1.1em;font-weight:600;padding-bottom:4px} .teacher{padding-bottom:24px} @media(max-width:1450px){.schedule{grid-template-columns:repeat(3,1fr)!important}} @media(max-width:1110px){.schedule{grid-template-columns:repeat(2,1fr)!important}.schedule > div{margin:auto}} @media(max-width:778px){#header-title{font-size:medium}.title-s{font-size:x-small}.schedule{grid-template-columns:1fr !important;gap:5px}.schedule > div{min-width:0;max-width:100%;overflow-x:auto !important;margin:1em 0}}</style>
<header><h3 id="header-title">BoostBot BoostLearn BoostMind</h3><button id="burger" hidden>≡</button></header><div class="title-s"><h1>Расписание занятий</h1></div><div class="schedule">{main}</div></body></html>"""


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