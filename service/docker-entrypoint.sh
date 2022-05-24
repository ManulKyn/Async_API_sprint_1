#!/bin/bash

while ! nc -z ${REDIS_HOST} 6379; do
    sleep 5
    echo "still waiting for redis ..."
done

echo "redis launched"

while ! nc -z ${ELASTIC_HOST} 9200; do
    sleep 5
    echo "still waiting for elastic ..."
done

echo "elastic launched"

while ! nc -z ${DB_HOST} ${DB_PORT}; do
    sleep 5
    echo "still waiting for postgres ..."
done

echo "postgres launched"




# Start server
echo "Starting server"
#uvicorn main:app --host 0.0.0.0 --port 8000
python main.py
