# modified from
# https://www.raspberrypi.org/learning/sense-hat-data-debug_logger/code/Sense_Logger_v4.py

# free space on SD card is 24097.036 mB
# Each image takes up 23.2 mB
# Therefore, there is space for 988.226721517 images, or 900 images to be safe

# package imports
import os
from time import sleep, time, strftime

# Raspberry Pi hardware imports
import picamera
import picamera.array
from sense_hat import SenseHat

# initialize SenseHat
sensehat = SenseHat()

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

# write header
with open(sensor_log_path, 'w') as sensor_log:
    sensor_log.write(
        'DateTime,Temp_h,Temp_p,Humidity,Pressure,Yaw,Pitch,Roll,Mag_x,Mag_y,Mag_z,Accel_x,Accel_y,Accel_z,Gyro_x,Gyro_y,Gyro_z,Message' + '\n')

# define function to return a csv line of all sensehat data


def get_sensehat_data():
    output_data = []

    output_data.append(sensehat.get_temperature_from_humidity())
    output_data.append(sensehat.get_temperature_from_pressure())
    output_data.append(sensehat.get_humidity())
    output_data.append(sensehat.get_pressure())

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

    # return output data in CSV format
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

with picamera.PiCamera() as camera:
    # set to maximum v2 resolution
    camera.resolution = (3280, 2464)
    append_csv(sensor_log_path, get_sensehat_data() + ['Camera initialized'])

    # continue until timeout is exceeded
    while time() < logging_start_time + timeout_seconds:
        # begin pre capture sensor log
        current_start_time = time()
        append_csv(sensor_log_path, get_sensehat_data() + [''])
        current_duration = time() - current_start_time
        sleep((picamera_capture_interval / 3) - current_duration)

        # begin capture sensor log
        current_start_time = time()
        image_name = os.path.join(log_dir, strftime(
            '%Y%m%d_%H%M%S_%Z') + '_rgb' + '.bip')
        append_csv(sensor_log_path, get_sensehat_data() +
                   ['RGB image captured to ' + image_name])
        # capture unencoded RGB directly to binary file
        with open(image_name, 'wb') as binary_file:
            camera.capture(binary_file, 'rgb')
        current_duration = time() - current_start_time
        sleep((picamera_capture_interval / 3) - current_duration)

        # begin post capture sensor log
        current_start_time = time()
        append_csv(sensor_log_path, get_sensehat_data() + [''])
        current_duration = time() - current_start_time
        sleep((picamera_capture_interval / 3) - current_duration)

append_csv(sensor_log_path, get_sensehat_data() + ['Log end'])
