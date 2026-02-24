FROM python:3.12-slim

WORKDIR /boost-ip/src/

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . . 

USER daemon

CMD [ "python", "main.py" ]