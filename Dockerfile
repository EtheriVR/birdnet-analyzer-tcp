FROM tensorflow/tensorflow:2.19.0

RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app

COPY requirements.txt ./requirements.txt

RUN pip3 install -r requirements.txt
COPY birdserver.py ./birdserver.py

ENV LON=59.3
ENV LAT=17.1

CMD python3 -u birdserver.py ${LAT} ${LON}
