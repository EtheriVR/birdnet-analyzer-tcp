from birdnetlib import RecordingBuffer
from birdnetlib.analyzer import Analyzer
import birdnetlib.wavutils as wavutils
from datetime import datetime
from pprint import pprint
import argparse
import socketserver

class MyTCPHandler(socketserver.StreamRequestHandler):
    def handle(self):
        analyzer = Analyzer()
        # Read WAV data from the socket
        for rate, data in wavutils.bufferwavs(self.rfile):
            # Make a RecordingBuffer with buffer and rate
            recording = RecordingBuffer(
                analyzer,
                data,
                rate,
                lat=self.server.lat,
    		    lon=self.server.lon,
                date=datetime.date.today(),
                min_conf=0.25,
            )
            recording.analyze()
            pprint(recording.detections)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Birdnetlib server with lat/lon arguments")
    parser.add_argument("latitude", type=float, help="Latitude for the recording location")
    parser.add_argument("longitude", type=float, help="Longitude for the recording location")
    args = parser.parse_args()  # Parse the arguments
    try:
        with socketserver.TCPServer(("0.0.0.0", 9988), MyTCPHandler) as server:
            server.lat = args.latitude  
            server.lon = args.longitude
            print(f"birdnet-analyzer listening for audio at location {args.latitude}, {args.longitude} ")
            server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()