FROM python:3.9-slim-buster

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y gunicorn

WORKDIR /code

COPY requirements.txt .
RUN pip install --upgrade pip --no-cache-dir && pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["python", "-m", "gunicorn", "main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
