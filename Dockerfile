FROM python:3.12-slim

RUN apk add --no-cache curl

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY src/ ./src/
COPY config/ ./config/

EXPOSE 8000

CMD ["python", "src/main.py"]
