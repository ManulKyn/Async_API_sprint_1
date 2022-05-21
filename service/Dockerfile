FROM python:3.9-slim-buster

WORKDIR /code

COPY requirements.txt .
RUN pip install --upgrade pip --no-cache-dir && pip install -r requirements.txt --no-cache-dir

COPY . .

# RUN chmod +x ./entrypoint.sh
# ENTRYPOINT ["./entrypoint.sh"]
EXPOSE 8000/tcp
# CMD ["uvicorn", "main:app", "--reload"]
# CMD ["python", "main.py"]
CMD uvicorn main:app --host 0.0.0.0 --port 8000 --reload