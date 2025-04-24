# birdnet-analyzer-tcp
A birdnet analyzer that listens on TCP audio stream


Run the listener


`docker run -it -p 9988:9988 --network birdnet --name birdnet-analyzer --hostname birdnet-analyzer -e LON=17.12 -e LAT=58.65 birdnet:latest`

Run the audio source


`docker run -it -e PULSE_SERVER=unix:${XDG_RUNTIME_DIR}/pulse/native  -v ${XDG_RUNTIME_DIR}/pulse/native:${XDG_RUNTIME_DIR}/pulse/native  -v ~/.config/pulse/cookie:/root/.config/pulse/cookie --network birdnet birdnet-audio:latest`

