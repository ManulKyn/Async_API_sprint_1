#!/bin/bash

echo "trying to connect to db"

while ! nc -z ${DB_HOST} 5432; do
    sleep 5
    echo "still waiting for db ..."
done

echo "db launched"

echo "trying to connect to elastic"

echo
while ! nc -z ${ELASTICSEARCH_HOST} 9200; do
    sleep 5
    echo "still waiting for elastic ..."
done

echo "elastic launched"

python main.py
