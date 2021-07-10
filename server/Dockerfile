FROM nvcr.io/nvidia/cuda:11.3.1-cudnn8-runtime-ubuntu20.04

RUN apt-get update && \
  DEBIAN_FRONTEND=noninteractive apt-get install -y python3-pip

COPY ./requirements.txt /app/requirements.txt

RUN pip install --upgrade pip
RUN pip install gunicorn
RUN pip install -r /app/requirements.txt

COPY . /app

WORKDIR /app

RUN rm -f .env