FROM python:3.8

RUN apt-get update && apt-get install -y netcat

ENV PYTHONUNBUFFERED=1

COPY etl_app/requirements.txt .
RUN /usr/local/bin/python -m pip install --upgrade pip && pip install -r requirements.txt
COPY etl_app ./etl_app

WORKDIR ./etl_app

CMD ["python", "main.py"]
