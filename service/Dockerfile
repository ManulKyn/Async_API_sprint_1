FROM python:3.9-slim-buster

RUN apt-get update && apt-get install -y netcat

ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY requirements.txt .
RUN pip install --upgrade pip --no-cache-dir && pip install -r requirements.txt --no-cache-dir

COPY . .

COPY ./docker-entrypoint.sh ./docker-entrypoint.sh

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
