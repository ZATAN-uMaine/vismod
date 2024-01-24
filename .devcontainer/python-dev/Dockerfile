FROM python:3.11-bookworm

RUN apt-get update && apt-get install -y ansible ansible-lint
RUN adduser --uid 1000 --disabled-password --gecos "" work
