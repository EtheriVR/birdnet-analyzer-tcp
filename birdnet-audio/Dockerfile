FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y alsa-utils
RUN apt-get update && apt-get install -y pulseaudio
RUN apt-get update && apt-get install -y netcat-traditional

WORKDIR /app
CMD ["/bin/bash","-c","arecord -r 48000 -f FLOAT_LE --max-file-time 10 | nc.traditional birdnet-analyzer 9988"]