#!/usr/bin/python3
import threading
import gpsd
import time

def record_gps():
    gpsd.connect()
    while True:
        try:
            data = gpsd.get_current()
            print({
                "src": "gps",
                "time": time.time(),
                "lat": data.lat,
                "lon": data.lon,
                "alt": data.alt,
                "hspeed": data.hspeed,
                "track": data.track,
                "climb": data.climb,
                "error": data.error,
                "time": data.time,
                "mode": data.mode,
                "sats": data.sats,
            })
            time.sleep(0.1)
        except Exception as e:
            print("{}".format(e))


gps_thread = threading.Thread(target=record_gps)
gps_thread.start()
print("Capturing data...")
