FROM python:3.11-slim

RUN apt update && apt upgrade -y
COPY frontend/requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

COPY /frontend /app/frontend

WORKDIR /app/frontend
CMD python app.py
