from openai import OpenAI
from dotenv import load_dotenv 
import os
from datetime import datetime
import services.get_weeks as get_weeks
from pathlib import Path
import random as rnd

load_dotenv()


try:
    api_key = os.getenv("AI_TOKEN")
except EnvironmentError as e:
    print(e)
    pass


client = OpenAI(base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )



model1 = "arcee-ai/trinity-large-preview:free"#WORKS 1.8789713382720947-10s
# model2 = "openai/gpt-oss-120b:free"#WORKS 15.933915376663208s
model2 = "openai/gpt-oss-20b:free"#WORKS 3.6755878925323486s
# model03 = "qwen/qwen3-next-80b-a3b-instruct:free" #DOESNT WORK
# model03_2 = "qwen/qwen3-4b:free" #DOESNT WORK
model3 = "google/gemma-3-4b-it:free" #WORKS 3.1092631816864014 
#model4 = "stepfun/step-3.5-flash:free" #works
model4 = "baidu/cobuddy:free"

mapping_models = {
    1:model1,
    2:model2,
    3:model3,
    4:model4
}

m = [
    model1, model2, model3, model4
]

# Список актуальных бесплатных моделей на OpenRouter
# Включает в себя проверенные вами и новые стабильные эндпоинты
FREE_MODELS = [
    "arcee-ai/trinity-large-preview:free",           # Проверено вами: быстрый инференс (~2с)
    "arcee-ai/trinity-large-thinking:free",          # Новая версия с цепочкой рассуждений
    "openai/gpt-oss-20b:free",                      # Проверено вами: стабильный баланс скорости
    "openai/gpt-oss-120b:free",                     # Тяжелая, но точная (может быть медленной)
    "google/gemma-3-4b-it:free",                    # Проверено вами: очень легкая и быстрая
    "google/gemma-3-27b-it:free",                   # Более умная версия Gemma
    "meta-llama/llama-4-scout:free",                # Новинка: замена Llama 3.1, оптимизирована под скорость
    "meta-llama/llama-3.3-70b-instruct:free",       # Классика, всё еще стабильна
    "deepseek/deepseek-v4-flash:free",              # Идеальна для YES/NO задач (минимальный пинг)
    "mistralai/mistral-small-3.1-24b-instruct:free", # Хорошо понимает JSON и четкие инструкции
    "qwen/qwen3-coder:free",                        # Если нужно анализировать код расписания
    "minimax/minimax-m2.5:free",                    # Высокая пропускная способность
    "nvidia/nemotron-3-super-120b-a12b:free",       # Отличная логика, MoE архитектура
    "baidu/cobuddy:free",                           # Проверено вами: стабильный эндпоинт от Baidu
    "z-ai/glm-4.5-air:free",                        # Легкая модель с хорошим пониманием русского
    "openrouter/free"                               # Авто-роутер (выбирает лучшую доступную сам)
]


def parse_ai_response(response) -> bool:
    message = response.choices[0].message

    content = message.content

    if not content and hasattr(message, 'reasoning') and message.reasoning:
        content = message.reasoning
        
    
    if not content:
        content = getattr(message, 'reasoning', "") or ""

    if not content:
        return False

    res = content.strip().upper()
    return "YES" in res or "ДА" in res


def answer_text(ctx:str, model:str = None) -> bool | None:
    try:
        model = model if model else "openrouter/free"

        response = client.chat.completions.create(
            model=model,
            messages=[
                
                {
                    "role": "user",
                    "content": f"""Студенческий чат.
Ты — лингвистический анализатор для бота студенческого расписания. Твоя задача: понять, запрашивает ли пользователь учебный график.

Контекст: Ты работаешь в чате студентов/школьников. Любое упоминание учебных предметов (математика, история, право и т.д.) в вопросительном контексте относится к расписанию.

Критерии ДА (YES):
- Прямые запросы («скинь расписание», «какие завтра пары?»).
- Упоминание конкретных предметов + вопрос («где сейчас история?», «а когда будет матан?», «есть сегодня физика?»).
- Вопросы о времени или месте («какая аудитория?», «во сколько начало?», «что у нас следующим уроком?», «где мы сейчас?»).
- Сленг («че по парам?», «какая вилка?», «расп», «допы»).
- Уточнение дня недели («что в понедельник?», «завтра ко скольки?»).

Критерии НЕТ (NO):
- Обсуждение предмета без цели узнать время/место («я не выучил историю», «физика — это сложно»).
- Флуд, мемы, приветствия («всем привет», «кто идет курить?»).
- Личные вопросы («ты кто?», «как дела?»).

Формат ответа:
Отвечай СТРОГО одним словом: YES или NO.

Сообщение для анализа: 
{ctx}"""
                }
            ], max_tokens=50,
            temperature=0.1,
        )
        #print(response)
        return parse_ai_response(response)
    
    except Exception as e:
        print("ai.py, 122")
        print(e)

        try:
            answer_text(ctx, rnd.choice(FREE_MODELS))
        except Exception as e:
            print("ai, 128")
            print(e)

days_name = {0:"Понедельник", 1:"Вторник", 2:"Среда", 3:"Четверг", 4:"Пятница", 5:"Суббота", 6:"Воскресенье"}

def answer_text_with_fallback(ctx:str, data:str, model:str = "openrouter/free") -> bool | None:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": f"""Ты — лингвистический анализатор и консьерж для бота студенческого расписания. Твоя задача: понять интент (намерение) пользователя и сформировать сверхкраткий ответ, строго опираясь на предоставленные исходные данные.

### КОНТЕКСТ И ВРЕМЕННЫЕ ОРИЕНТИРЫ:
- Любое упоминание учебных предметов (математика, право и т.д.) в вопросительном контексте — это запрос расписания.
- Используй эти переменные для вычисления "сегодня/завтра/вчера" и типа недели:
  * Текущая дата и время: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} ({days_name[datetime.now().weekday()]})
  * Текущая неделя: {get_weeks.now_is}
  * Прошедшая неделя: {get_weeks.prev}
  * Следующая неделя: {get_weeks.next}

### ИСХОДНЫЕ ДАННЫЕ РАСПИСАНИЯ:
{data}

(воскресенье не отображается в расписании, если его нет в данных, значит пар в этот день нет - это выходной)

### ЗАПРОС ПОЛЬЗОВАТЕЛЯ:
"{ctx}"

### СТРОГИЕ ПРАВИЛА ДЛЯ ОТВЕТА:
1. Соотнеси запрос пользователя с текущей датой и типом недели. Пойми, какой день или предмет он ищет.
2. Вытащи из "ИСХОДНЫХ ДАННЫХ" только релевантные пары (название, аудитория, время). 
3. Формат ответа должен быть максимально лаконичным. Используй маркер времени и список пар.
4. Разрешено добавить вводную фразу (например: "Сейчас у вас:", "Завтра по расписанию:") длиной НЕ БОЛЕЕ 2-3 слов.
5. Никакой лишней вежливости, приветствий, размышлений и финальных фраз. Только факты из расписания.
6. Если запрос абсолютно не связан с расписанием, если указанного дня/предмета нет в данных или интент полностью непонятен — ответь строго одним словом: НЕПОНЯТНО

### ПРИМЕРЫ ДЛЯ ПОДРАЖАНИЯ:
Пользователь: "какие завтра пары?"
Ответ: "Завтра: Математика (ауд. 101), Физика (ауд. 202)"

Пользователь: "где сейчас история?"
Ответ: "Сейчас идет: История (ауд. 303)"

Пользователь: "че по расписанию в среду на след неделе"
Ответ: "В следующую среду: Программирование (ауд. 404), Лингвистика (ауд. 102) / ничего нет."

Пользователь: "привет, как дела, что делаешь?"
Ответ: "НЕПОНЯТНО"

ПОМНИ - ТЫ БОТ РАСПИСАНИЯ, ТВОЯ РОЛЬ - ДАВАТЬ КОНКРЕТНЫЕ ОТВЕТЫ ИСКЛЮЧИТЕЛЬНО НА ОСНОВЕ ПРЕДОСТАВЛЕННЫХ ДАННЫХ. НЕ ВЫХОДИ ЗА ИХ ПРЕДЕЛЫ.
"""
                }
            ], max_tokens=600,
            temperature=0.1,
        )
        # print(days_name[datetime.now().weekday()])
        # print(data)
        # print(response)
        return response.choices[0].message.content
    except Exception as e:
        # answer_text_with_fallback(ctx, data, "openrouter/free")
        print("ai.py, 161")
        print(e)