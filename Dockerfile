# Dockerfile

# pull the official docker image
FROM mirror.gcr.io/library/python:3.11.1-slim

# set work directory
WORKDIR /app

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2

RUN apt-get -y install arp-scan

# install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .
