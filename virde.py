# modified from https://www.raspberrypi.org/learning/sense-hat-data-logger/code/Sense_Logger_v4.py

# imports
from time import time
from datetime import datetime
from threading import Thread
from time import sleep

from sense_hat import SenseHat

# define logging interval in seconds
logging_interval = 1

# define name of logfile
filename = "log"

# append datetime to filename
filename = filename + "_" + str(int(time.time())) + ".csv"

# define function to return a csv line of all sensehat data
def get_sensehat_csv_line(sensehat):
    output_data = [datetime.now()]

    output_data.append(sensehat.get_temperature_from_humidity())
    output_data.append(sensehat.get_temperature_from_pressure())
    output_data.append(sensehat.get_humidity())
    output_data.append(sensehat.get_pressure())

    orientation = sensehat.get_orientation()
    output_data.extend([orientation["yaw"], orientation["pitch"], orientation["roll"]])

    magnetometer = sensehat.get_compass_raw()
    output_data.extend([magnetometer["x"], magnetometer["y"], magnetometer["z"]])

    accelerometer = sensehat.get_accelerometer_raw()
    output_data.extend([accelerometer["x"], accelerometer["y"], accelerometer["z"]])

    gyroscope = sensehat.get_gyroscope_raw()
    output_data.extend([gyroscope["x"], gyroscope["y"], gyroscope["z"]])

    # return output data in comma separated form
    return ",".join(str(value) for value in output_data)

# construct logfile header
header = ["datetime"]
header.append("temp_h")
header.append("temp_p")
header.append("humidity")
header.append("pressure")
header.extend(["pitch", "roll", "yaw"])
header.extend(["mag_x", "mag_y", "mag_z"])
header.extend(["accel_x", "accel_y", "accel_z"])
header.extend(["gyro_x", "gyro_y", "gyro_z"])

# instantiate sensehat object
sensehat = SenseHat()

# open logfile
with open(filename, "a") as logfile:
    # write header to logfile
    logfile.write(",".join(str(value) for value in header) + "\n")
    
    # main loop
    while True:     
        logfile.write(+"\n")
        sleep(logging_interval)
