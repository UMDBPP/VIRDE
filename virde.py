#!/usr/bin/env python3
# modified from
# https://www.raspberrypi.org/learning/sense-hat-data-debug_logger/code/Sense_Logger_v4.py

# free space on SD card is 24097.036 mB
# Each image takes up 23.2 mB
# Therefore, there is space for 988.226721517 images, or 900 images to be safe

# package imports
import os
from time import time, strftime, sleep

# Raspberry Pi hardware imports
import picamera
from sense_hat import SenseHat
import gpsd

# initialize SenseHat
sensehat = SenseHat()

# initialize Ultimate GPS HAT
gpsd.connect()

# define camera capture interval
picamera_capture_interval = 6

# average flight time is 98.92 minutes, longest ever flight was 175.53 minutes
timeout_seconds = 60 * 225

# define path to log directory
log_dir = os.path.join('/home/pi/Desktop', 'virde_log',
                       strftime('%Y%m%d_%H%M%S_%Z'))

# create path to log directory if it doesn't exist
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

# define log file path
sensor_log_path = os.path.join(log_dir, strftime(
    '%Y%m%d_%H%M%S_%Z') + '_sensor_log.csv')
gps_log_path = os.path.join(log_dir, strftime(
    '%Y%m%d_%H%M%S_%Z') + '_gps_log.csv')

# write header
with open(sensor_log_path, 'w') as sensor_log:
    sensor_log.write(
        'DateTime,Yaw,Pitch,Roll,Mag_x,Mag_y,Mag_z,Accel_x,Accel_y,Accel_z,Gyro_x,Gyro_y,Gyro_z,Temp_h,Temp_p,Humidity,Pressure,Message' + '\n')

with open(gps_log_path, 'w') as gps_log:
    gps_log.write(
        'DateTime,GPS_Time,Longitude,Latitude,Altitude_m,Tim_unc,Lon_unc,Lat_unc,Alt_unc' + '\n')


# define function to return a csv line of all sensehat data


def get_sensehat_data():
    output_data = []

    orientation = sensehat.get_orientation()
    output_data.extend(
        [orientation['yaw'], orientation['pitch'], orientation['roll']])

    magnetometer = sensehat.get_compass_raw()
    output_data.extend(
        [magnetometer['x'], magnetometer['y'], magnetometer['z']])

    accelerometer = sensehat.get_accelerometer_raw()
    output_data.extend(
        [accelerometer['x'], accelerometer['y'], accelerometer['z']])

    gyroscope = sensehat.get_gyroscope_raw()
    output_data.extend([gyroscope['x'], gyroscope['y'], gyroscope['z']])

    output_data.append(sensehat.get_temperature_from_humidity())
    output_data.append(sensehat.get_temperature_from_pressure())
    output_data.append(sensehat.get_humidity())
    output_data.append(sensehat.get_pressure())

    # return output data in CSV format
    return output_data


def get_gps_data():
    gps_data = gpsd.get_current()
    output_data = []

    gps_error = gps_data.error

    output_data.append(time())
    output_data.append(gps_data.time)
    output_data.append(gps_data.lon)
    output_data.append(gps_data.lat)
    output_data.append(gps_data.alt)
    output_data.append(gps_error['t'])
    output_data.append(gps_error['x'])
    output_data.append(gps_error['y'])
    output_data.append(gps_error['v'])

    return output_data


def append_csv(filename, input_data):
    output_line = strftime('%Y-%m-%d %H:%M:%S %Z') + ','

    if isinstance(input_data, str):
        output_line += input_data
    else:
        output_line += ','.join(str(value) for value in input_data)

    with open(filename, 'a') as csv_file:
        csv_file.write(output_line + '\n')


# note starting time
logging_start_time = time()
append_csv(sensor_log_path, get_sensehat_data() + ['Log start'])
append_csv(gps_log_path, get_gps_data())

with picamera.PiCamera() as camera:
    # set to maximum v2 resolution
    camera.resolution = (3280, 2464)
    append_csv(sensor_log_path, get_sensehat_data() + ['Camera initialized'])

    # continue until timeout is exceeded
    while time() < logging_start_time + timeout_seconds:
        # begin pre capture sensor log
        current_start_time = time()

        append_csv(sensor_log_path, get_sensehat_data() + [''])
        append_csv(gps_log_path, get_gps_data())
        current_duration = time() - current_start_time
        sleep((picamera_capture_interval / 3) - current_duration)

        # begin capture sensor log
        current_start_time = time()
        image_name = os.path.join(log_dir, strftime(
            '%Y%m%d_%H%M%S_%Z') + '_rgb' + '.bip')

        append_csv(sensor_log_path, get_sensehat_data() +
                   ['RGB image captured to ' + image_name])
        append_csv(gps_log_path, get_gps_data())

        # capture unencoded RGB directly to binary file
        with open(image_name, 'wb') as binary_file:
            camera.capture(binary_file, 'rgb')
        current_duration = time() - current_start_time
        sleep((picamera_capture_interval / 3) - current_duration)

        # begin post capture sensor log
        current_start_time = time()

        append_csv(sensor_log_path, get_sensehat_data() + [''])
        append_csv(gps_log_path, get_gps_data())

        current_duration = time() - current_start_time
        sleep((picamera_capture_interval / 3) - current_duration)

append_csv(sensor_log_path, get_sensehat_data() + ['Log end'])
append_csv(gps_log_path, get_gps_data())
