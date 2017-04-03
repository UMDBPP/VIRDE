# modified from https://www.raspberrypi.org/learning/sense-hat-data-debug_logger/code/Sense_Logger_v4.py

# package imports
import os
from time import sleep, time
import logging
import numpy

# Raspberry Pi hardware imports
import picamera
import picamera.array
from sense_hat import SenseHat

sensehat = SenseHat()

# define interval in seconds between each image capture
picamera_capture_interval = 3

start_time = time()
timeout = 30

# define path to log directory
log_dir = os.path.join('/home/pi/Desktop', 'virde_log', 'log_' + str(int(start_time)))

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
events_file_handler.setFormatter(logging.Formatter('%(asctime)s,%(levelname)s,%(message)s'))
sensor_file_handler.setFormatter(logging.Formatter('%(asctime)s,%(message)s'))
images_file_handler.setFormatter(logging.Formatter('%(asctime)s,%(message)s'))

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
        events_logger.debug('Appended line to sensor log')
        sleep(1)

# define starting time for thread completion
start_time = time()

# log script start
events_logger.info('Started logging')

with picamera.PiCamera() as camera:
    # set to maximum v2 resolution
    camera.resolution = (3280, 2464)
    while time() < start_time + timeout:              
        # let automatic exposure settle for 2 seconds
        sleep_while_logging(2)

        # capture PNG image after processing
        image_name = os.path.join(log_dir, 'image_' + str(int(time())) + '.png')
        camera.capture(image_name)
        
        # log image save
        images_logger.info(image_name)
        events_logger.debug('Captured PNG image')

        # let automatic exposure settle for 2 seconds
        sleep_while_logging(2)
        
        # capture unencoded RGB directly to binary file
        image_name = os.path.join(log_dir, 'rgb_' + str(int(time())) + '.bip')
        with open(image_name, 'wb') as binary_file:
            camera.capture(binary_file, 'rgb')
        
        # log image save
        images_logger.info(image_name)
        events_logger.debug('Captured RGB image')

        # let automatic exposure settle for 2 seconds
        sleep_while_logging(2)
        
        # capture Bayer data to binary file after demosaicing
        image_name = os.path.join(log_dir, 'bayer_' + str(int(time())) + '.bip')
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
        events_logger.debug('Captured Bayer image')

# log script completion
events_logger.info('Finished logging')
