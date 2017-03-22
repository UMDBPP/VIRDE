# modified from https://www.raspberrypi.org/learning/sense-hat-data-logger/code/Sense_Logger_v4.py

# imports
import os
from datetime import datetime
from threading import Thread
from time import sleep, time
import logging

#import pygame
#from pygame.locals import *
from sense_hat import SenseHat
from picamera import PiCamera

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
logging.info('Starting script...')

# instantiate sensehat and pygame
sensehat = SenseHat()
#pygame.init()

# define logging intervals in seconds
sensehat_logging_interval = 1
picamera_logging_interval = 6

timeout = picamera_logging_interval * 20
start_time = time()

# define path to log directory
log_dir = '/home/pi/Desktop/virde_log/'

# create path to log directory if it doesn't exist
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

# define image directory
image_dir = os.path.join(log_dir, 'images_' + str(int(start_time)))

# create image directory if it doesn't exist
if not os.path.exists(image_dir):
    os.mkdir(image_dir)
            
# append datetime to filename and open logfile with append connection
sensor_log_file = open(os.path.join(log_dir, 'sensor_log_' + str(int(start_time)) + '.csv'), 'a')

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
sensor_log_file.write(','.join(str(value) for value in header) + '\n')

# define function to return a csv line of all sensehat data
def get_sensehat_csv_line(sensehat):
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

def picamera_capture():
    with PiCamera(sensor_mode = 2) as camera:
        camera.resolution = (3280, 2464)
    
        # let automatic exposure settle
        sleep(1)

        image_name = 'image_' + str(int(time()))
        # capture in PNG format at native resolution
        camera.capture(os.path.join(image_dir, image_name + '.png'))
        logging.info('Saved image ' + image_name + '.png')
        
        # capture in unencoded RGB format
        camera.capture(os.path.join(image_dir, 'image_' + image_name + '.data'), 'rgb')
        logging.info('Saved image ' + image_name + '.data')

def sensehat_logging_thread():
    while time() < start_time + timeout:
        sensor_log_file.write(get_sensehat_csv_line(sensehat) + '\n')
        logging.info('Appended line to ' + sensor_log_file)
        sleep(sensehat_logging_interval)
      
def picamera_logging_thread():
    while time() < start_time + timeout:
        # capture image
        picamera_capture()

        # delay the specified interval
        sleep(picamera_logging_interval - 1)

# start logging threads
Thread(target = sensehat_logging_thread).start()
Thread(target = picamera_logging_thread).start()

###print("starting input loop")
##
##while True:#time() < start_time + timeout:
##    for event in pygame.event.get():
##        if event.type == KEYDOWN:
##            if event.key == K_RIGHT:
##                print("Taking picture")
##                for second in range(10, 0):
##                    sensehat.show_letter(str(second))
##                    print(str(second))
##                    sensor_log_file.write(get_sensehat_csv_line(sensehat) + '\n')
##                    sleep(1)
##                picamera_capture()
##                sensehat.clear()

#sensehat.show_message("DONE")
