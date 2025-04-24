from birdnetlib import RecordingBuffer
from birdnetlib.analyzer import Analyzer
import birdnetlib.wavutils as wavutils
from datetime import date
from pprint import pprint
import argparse
import socketserver
import requests
import json


class MyTCPHandler(socketserver.StreamRequestHandler):
    def handle(self):
        analyzer = Analyzer()
        api_url = "http://bird-api_server:8080/data"
        # Read WAV data from the socket
        for rate, data in wavutils.bufferwavs(self.rfile):
            # Make a RecordingBuffer with buffer and rate
            recording = RecordingBuffer(
                analyzer,
                data,
                rate,
                lat=self.server.lat,
    		    lon=self.server.lon,
                date=date.today(),
                min_conf=0.25,
            )
            recording.analyze()

            for detection in recording.detections:
                payload = {
                    "name": detection['common_name'],
                    "confidence": detection['confidence']
                }
                print("Detected: ")
                print(detection['common_name'])
                print(detection['confidence'])
                try:
                    response = requests.post(api_url, json=payload, timeout=1)
                    try:
                        response_data = response.json()
                        print("Response Body (JSON):")
                        print(json.dumps(response_data, indent=2))
                    except json.JSONDecodeError:
                        # If the response isn't valid JSON, print it as text
                        print("Response Body (non-JSON):")
                        print(response.text)
                except Exception as e:
                    print("Failed to post to database!")


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