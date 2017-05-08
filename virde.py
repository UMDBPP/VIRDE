# modified from https://www.raspberrypi.org/learning/sense-hat-data-debug_logger/code/Sense_Logger_v4.py

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

sensehat = SenseHat()

# define camera capture interval
picamera_capture_interval = 20

# average flight time is 98.92 minutes
timeout = 60 * 110

# define path to log directory
log_dir = os.path.join('/home/pi/Desktop', 'virde_log', 'log_' + strftime("%Y%m%d_%H%M%S_%Z"))

# create path to log directory if it doesn't exist
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

# add headers to log files
with open(os.path.join(log_dir, 'events.log'), 'w') as events_log:
    events_log.write('DateTime,Message' + '\n')
with open(os.path.join(log_dir, 'sensor.log'), 'w') as sensor_log:
    sensor_log.write('DateTime,Temp_h,Temp_p,Humidity,Pressure,Pitch,Roll,Yaw,Mag_x,Mag_y,Mag_z,Accel_x,Accel_y,Accel_z,Gyro_x,Gyro_y,Gyro_z' + '\n')
with open(os.path.join(log_dir, 'images.log'), 'w') as images_log:
    images_log.write('DateTime,ImagePath' + '\n')

# create loggers
events_logger = logging.getLogger('events')
sensor_logger = logging.getLogger('sensor')
images_logger = logging.getLogger('images')

# set logging levels
events_logger.setLevel(logging.DEBUG)
sensor_logger.setLevel(logging.INFO)
images_logger.setLevel(logging.INFO)

# create file handlers
events_file_handler = logging.FileHandler(os.path.join(log_dir, 'events.log'))
sensor_file_handler = logging.FileHandler(os.path.join(log_dir, 'sensor.log'))
images_file_handler = logging.FileHandler(os.path.join(log_dir, 'images.log'))

# set file handler logging levels
events_file_handler.setLevel(logging.DEBUG)
sensor_file_handler.setLevel(logging.DEBUG)
images_file_handler.setLevel(logging.DEBUG)

# add formatters to the file handlers
events_file_handler.setFormatter(logging.Formatter(strftime("%Y-%m-%d %H:%M:%S %Z") + ',%(levelname)s,%(message)s'))
sensor_file_handler.setFormatter(logging.Formatter(strftime("%Y-%m-%d %H:%M:%S %Z") + ',%(levelname)s,%(message)s'))
images_file_handler.setFormatter(logging.Formatter(strftime("%Y-%m-%d %H:%M:%S %Z") + ',%(levelname)s,%(message)s'))

# add file handlers to the loggers
events_logger.addHandler(events_file_handler)
sensor_logger.addHandler(sensor_file_handler)
images_logger.addHandler(images_file_handler)

# define function to return a csv line of all sensehat data
def get_sensehat_data_csv():
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

    # log sensor read
    events_logger.debug('Accessed sensor data')

    # return output data in CSV format
    return ','.join(str(value) for value in output_data)

def sleep_while_logging(seconds):
    for second in range(1, seconds + 1):
        sensor_logger.info(get_sensehat_data_csv())
        events_logger.info('Appended line to sensor log')
        sleep(1)

# log script start
events_logger.info('Started logging')

# define starting time
start_time = time()

# note that camera takes about 13 seconds to initialize
with picamera.PiCamera() as camera:
    # set to maximum v2 resolution
    camera.resolution = (3280, 2464)
    
    # continue until timeout is exceeded
    while time() < start_time + timeout:
#         # capture PNG image after processing
#         image_name = os.path.join(log_dir, 'image_' + strftime("%Y%m%d_%H%M%S_%Z") + '.png')
#         camera.capture(image_name)
#  
#         # log image save
#         images_logger.info(image_name)
#         events_logger.info('Captured PNG image')

        # capture unencoded RGB directly to binary file
        image_name = os.path.join(log_dir, strftime("%Y%m%d_%H%M%S_%Z") + '_rgb_' + '.bip')
        with open(image_name, 'wb') as binary_file:
            camera.capture(binary_file, 'rgb')

        # log image save
        images_logger.info(image_name)
        events_logger.info('Captured RGB image in BIP format (3296x2464 pixels)')

        # wait for delay time
        sleep_while_logging(picamera_capture_interval / 2)

        # capture Bayer data to binary file (after demosaicing)
        image_name = os.path.join(log_dir, strftime("%Y%m%d_%H%M%S_%Z") + '_bayer_' + '.bip')
        with picamera.array.PiBayerArray(camera) as stream:
            # capture to stream as bayer data
            camera.capture(stream, 'jpeg', bayer=True)

            # Demosaic data and write to output (just use stream.array if you want to skip the demosaic step)
            output = (stream.demosaic() >> 2).astype(numpy.uint8)

            # save to file
            with open(image_name, 'wb') as binary_file:
                output.tofile(binary_file)

        # log image save
        images_logger.info(image_name)
        events_logger.info('Captured Bayer data in BIP format (3280x2464 pixels)')

        # wait for delay time
        sleep_while_logging(picamera_capture_interval / 2)

# log script completion
events_logger.info('Finished logging')
