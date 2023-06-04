# base image
FROM python:3.10.11-alpine

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /srv/image-api

COPY requirements.txt .
RUN apk add bash  postgresql-client libpq-dev \
    && python -m pip install -U pip \
    && pip install -r requirements.txt

COPY . .
