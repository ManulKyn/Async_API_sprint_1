FROM python:3.8

RUN apt-get update && apt-get install -y netcat

ENV PYTHONUNBUFFERED=1

WORKDIR ./etl_app

COPY etl_app/requirements.txt .
RUN /usr/local/bin/python -m pip install --upgrade pip && pip install -r requirements.txt
COPY etl_app .

CMD ["python", "main.py"]
