FROM python:3.9-slim
WORKDIR /code
COPY requirements.txt .
RUN pip install --upgrade pip --no-cache-dir && pip install -r requirements.txt --no-cache-dir
COPY 01_etl/ .
CMD python etl.py
