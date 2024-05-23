FROM python:3.11-slim

RUN apt update && apt upgrade -y

COPY frontend/requirements.in /requirements.in

RUN pip install pip-tools && \
    pip-compile requirements.in && \
    pip-sync
 
COPY /frontend /app/frontend
 
WORKDIR /app/frontend
CMD python -m dash_app