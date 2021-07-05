FROM python:3.8.1
ADD . /python-flask
WORKDIR /python-flask
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y 
RUN pip install -r requirements.txt
