FROM python:3.8.16-slim

RUN apt update && \
  apt install -y git cmake libmagic-dev libgtk-3-dev

WORKDIR /app
COPY requirements.txt .
RUN pip install -U pip setuptools
RUN pip install -r requirements.txt

COPY . /app
ENV PYTHONPATH=.

EXPOSE 8080
CMD ["/bin/bash", "-c"]
