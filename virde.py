# modified from https://www.raspberrypi.org/learning/sense-hat-data-logger/code/Sense_Logger_v4.py

# imports
from datetime import datetime
from threading import Thread
from time import sleep, time

from sense_hat import SenseHat
from picamera import PiCamera

# instantiate hardware objects
sensehat = SenseHat()
camera = PiCamera()

# define logging intervals in seconds
sensehat_logging_interval = 1
picamera_logging_interval = 6

# define path to log directory
logdir = '~/Desktop/virde_log/'

# append datetime to filename and open logfile as append connection
logfile = open(logdir + 'log' + '_' + str(int(time.time())) + '.csv', 'a')

# construct logfile header
header = ['datetime']
header.append('temp_h')
header.append('temp_p')
header.append('humidity')
header.append('pressure')
header.extend(['pitch', 'roll', 'yaw'])
header.extend(['mag_x', 'mag_y', 'mag_z'])
header.extend(['accel_x', 'accel_y', 'accel_z'])
header.extend(['gyro_x', 'gyro_y', 'gyro_z'])

# write header to logfile
logfile.write(','.join(str(value) for value in header) + '\n')

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

def sensehat_logging_thread(logfile):
    while True:
        logfile.write(get_sensehat_csv_line(sensehat) + '\n')
        sleep(sensehat_logging_interval)
      
def picamera_logging_thread():
    while True:      
        # let automatic exposure settle
        camera.start_preview()
        sleep(3)
        
        # capture in PNG format at native resolution
        camera.capture(logdir + 'image' + '_' + str(int(time.time())) + '.png')
        
        # capture in unencoded RGB format
        camera.capture(logdir + 'image' + '_' + str(int(time.time())) + '.data', 'rgb')
        
        sleep(picamera_logging_interval)

# start logging threads
Thread(target = sensehat_logging_thread).start()
Thread(target = picamera_logging_thread).start()
