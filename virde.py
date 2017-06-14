# modified from https://www.raspberrypi.org/learning/sense-hat-data-debug_logger/code/Sense_Logger_v4.py

# free space on SD card is 24097.036 mB
# Each image takes up 23.2 mB 
# Therefore, there is space for 988.226721517 images, or 900 images to be safe

# package imports
import os
from time import sleep, time, strftime
from datetime import datetime
import logging
import numpy

# Raspberry Pi hardware imports
import picamera
import picamera.array
from sense_hat import SenseHat

# initialize SenseHat
sensehat = SenseHat()

# define camera capture interval
picamera_capture_interval = 15

# average flight time is 98.92 minutes, longest ever flight was 175.53 minutes
timeout_seconds = 60 #* 225

# define path to log directory
log_dir = os.path.join('/home/pi/Desktop', 'virde_log', 'log_' + strftime('%Y%m%d_%H%M%S_%Z'))

# create path to log directory if it doesn't exist
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

# add headers to log files
with open(os.path.join(log_dir, 'sensor.log'), 'w') as sensor_log:
    sensor_log.write('DateTime,Temp_h,Temp_p,Humidity,Pressure,Pitch,Roll,Yaw,Mag_x,Mag_y,Mag_z,Accel_x,Accel_y,Accel_z,Gyro_x,Gyro_y,Gyro_z' + '\n')
with open(os.path.join(log_dir, 'images.log'), 'w') as images_log:
    images_log.write('DateTime,ImagePath' + '\n')

# define function to return a csv line of all sensehat data
def get_sensehat_data_csv_line():
    output_data = []

    output_data.append(sensehat.get_temperature_from_humidity())
    output_data.append(sensehat.get_temperature_from_pressure())
    output_data.append(sensehat.get_humidity())
    output_data.append(sensehat.get_pressure())

    orientation = sensehat.get_orientation()
    output_data.extend([orientation['yaw'], orientation['pitch'], orientation['roll']])

    magnetometer = sensehat.get_compass_raw()
    output_data.extend([magnetometer['x'], magnetometer['y'], magnetometer['z']])

    accelerometer = sensehat.get_accelerometer_raw()
    output_data.extend([accelerometer['x'], accelerometer['y'], accelerometer['z']])

    gyroscope = sensehat.get_gyroscope_raw()
    output_data.extend([gyroscope['x'], gyroscope['y'], gyroscope['z']])

    # return output data in CSV format
    return ','.join(str(value) for value in output_data)

def append_csv(file, input_data):
    file.write(strftime('%Y-%m-%d %H:%M:%S %Z') + ',' + ','.join(input_data) + '\n')

append_csv(images_log, ['Log start'])

# define starting time
logging_start_time = time()

with picamera.PiCamera() as camera:
    # set to maximum v2 resolution
    camera.resolution = (3280, 2464)
       
    append_csv('Camera initialized')
    
    # continue until timeout is exceeded
    while time() < logging_start_time + timeout_seconds:
        # begin pre capture sensor log
        current_start_time = time()

        # log sensor data
        append_csv(sensor_log, get_sensehat_data_csv_line())

        current_duration = time() - current_start_time

        sleep((picamera_capture_interval / 3) - current_duration)
        
        current_start_time = time()
        
        # log sensor data
        append_csv(sensor_log, get_sensehat_data_csv_line())
        
        # capture unencoded RGB directly to binary file
        image_name = os.path.join(log_dir, strftime('%Y%m%d_%H%M%S_%Z') + '_rgb_' + '.bip')
        with open(image_name, 'wb') as binary_file:
            camera.capture(binary_file, 'rgb')

        # log image save
        append_csv(images_log, [image_name])
        
        # get the time it took to capture the most recent image
        current_duration = time() - current_start_time

        # wait for delay time
        sleep((picamera_capture_interval / 3) - current_duration)
        
        # begin post capture sensor log
        current_start_time = time()

        # log sensor data
        append_csv(sensor_log, get_sensehat_data_csv_line())

        current_duration = time() - current_start_time

        sleep((picamera_capture_interval / 3) - current_duration)

append_csv(images_log, ['Log end'])