FROM python:3.8

RUN apt-get update && apt-get install -y netcat

ENV PYTHONUNBUFFERED=1

WORKDIR ./etl_app

COPY requirements.txt .
RUN /usr/local/bin/python -m pip install --upgrade pip && pip install -r requirements.txt
COPY . .

RUN apt-get install dos2unix
RUN dos2unix ./docker-entrypoint-etl.sh

ENTRYPOINT [ "./docker-entrypoint-etl.sh" ]
