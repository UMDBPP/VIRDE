# modified from https://www.raspberrypi.org/learning/sense-hat-data-logger/code/Sense_Logger_v4.py

# imports
import os
from datetime import datetime
from threading import Thread
from time import sleep, time
import logging
import picamera
import picamera.array
from sense_hat import SenseHat
import numpy

sensehat = SenseHat()

# define logging intervals in seconds
sensehat_logging_interval = 1
picamera_logging_interval = 5

start_time = time()
timeout = 10

# define path to log directory
log_dir = '/home/pi/Desktop/virde_log/'

# create logger to log all escalated at and above INFO
logger = logging.getLogger('events logger')
logger.setLevel(logging.DEBUG)

# add a file handler
file_handler = logging.FileHandler(log_dir + 'events_log_' + str(int(start_time)) + '.csv')
file_handler.setLevel(logging.DEBUG)  # ensure all messages are logged to file

# create a formatter and set the formatter for the handler.
formatter = logging.Formatter('%(asctime)s,%(levelname)s,%(message)s')
file_handler.setFormatter(formatter)

# add the Handler to the logger
logger.addHandler(file_handler)

# create path to log directory if it doesn't exist
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

# define image directory
image_dir = os.path.join(log_dir, 'images_' + str(int(start_time)))

# create image directory if it doesn't exist
if not os.path.exists(image_dir):
    os.mkdir(image_dir)

# append datetime to filename and open logfile with append connection
sensor_log_filename = os.path.join(log_dir, 'sensor_log_' + str(int(start_time)) + '.csv')
logger.info('Created sensor log at ' + sensor_log_filename)

# construct CSV header
header = ['datetime']
header.append('temp_h')
header.append('temp_p')
header.append('humidity')
header.append('pressure')
header.extend(['pitch', 'roll', 'yaw'])
header.extend(['mag_x', 'mag_y', 'mag_z'])
header.extend(['accel_x', 'accel_y', 'accel_z'])
header.extend(['gyro_x', 'gyro_y', 'gyro_z'])

# write header to file
with open(sensor_log_filename, 'w') as sensor_log:
    sensor_log.write(','.join(str(value) for value in header) + '\n')

# define function to return a csv line of all sensehat data
def get_sensehat_csv_line():
    output_data = [datetime.now()]

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

    # return output data in comma separated form
    return ','.join(str(value) for value in output_data)

def sensehat_logging_thread():
    logger.info('Started sensor logging thread')
    while time() < start_time + timeout:
        with open(sensor_log_filename, 'a') as sensor_log:
            sensor_log.write(get_sensehat_csv_line() + '\n')
        logger.info('Appended line to ' + sensor_log_filename)
        sleep(sensehat_logging_interval)
    logger.info('Stopped sensor logging thread')
      
def picamera_logging_thread():
    logger.info('Started camera logging thread')
    while time() < start_time + timeout:
        with picamera.PiCamera(sensor_mode=2, resolution='3280x2464') as camera:
            # set values
            print(camera.sensor_mode)
            print(camera.resolution)  # = (3280, 2464)
            
            # let automatic exposure settle
            sleep(2)
            image_name = 'image_' + str(int(time()))
            
            # capture in PNG format at native resolution
            camera.capture(os.path.join(image_dir, image_name + '.png'))
            logger.info('Saved image ' + image_name + '.png')

            # let automatic exposure settle
            sleep(2)
            image_name = 'image_' + str(int(time()))

            # capture as unencoded RGB (after preprocessing) to binary file
            with open(os.path.join(image_dir, image_name + '.rgb'), 'wb') as binary_file:
                camera.capture(binary_file, 'rgb')
            
            logger.info('Saved image ' + image_name + '.rgb')

            # capture as demosaiced Bayer data (raw signal) to binary file
            with picamera.array.PiBayerArray(camera) as stream:
                camera.capture(stream, 'jpeg', bayer=True)
                # Demosaic data and write to output (just use stream.array if you
                # want to skip the demosaic step)
                output = (stream.demosaic() >> 2).astype(numpy.uint8)
                with open(os.path.join(image_dir, image_name + '_bayer.rgb'), 'wb') as binary_file:
                    output.tofile(binary_file)
        
        # delay the specified interval
        sleep(picamera_logging_interval - 4)
    logger.info('Stopped camera logging thread')

start_time = time()

# start logging threads
Thread(target=sensehat_logging_thread).start()
Thread(target=picamera_logging_thread).start()
