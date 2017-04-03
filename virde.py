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

# define formatter that adds header to first line
class FormatterWithHeader(logging.Formatter):
    def __init__(self, header, fmt=None, datefmt=None, style='%'):
        super().__init__(fmt, datefmt, style)
        self.header = header  # This is hard coded but you could make dynamic
        # Override the normal format method
        self.format = self.first_line_format

    def first_line_format(self, record):
        # First time in, switch back to the normal format function
        self.format = super().format
        return self.header + "\n" + self.format(record)

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
sensor_logger.setLevel(logging.DEBUG)
images_logger.setLevel(logging.DEBUG)

# create file handlers
events_file_handler = logging.FileHandler(os.path.join(log_dir, 'events.log'))
sensor_file_handler = logging.FileHandler(os.path.join(log_dir, 'sensor.log'))
images_file_handler = logging.FileHandler(os.path.join(log_dir, 'images.log'))

# set file handler logging levels
events_file_handler.setLevel(logging.DEBUG)
sensor_file_handler.setLevel(logging.INFO)
images_file_handler.setLevel(logging.INFO)

# add formatters to the file handlers
events_file_handler.setFormatter(logging.Formatter('%(asctime)s,%(message)s'))
sensor_file_handler.setFormatter(logging.Formatter('%(asctime)s,%(message)s'))
images_file_handler.setFormatter(logging.Formatter('%(asctime)s,%(message)s'))

# add file handlers to the loggers
events_logger.addHandler(events_file_handler)
sensor_logger.addHandler(sensor_file_handler)
images_logger.addHandler(images_file_handler)

# define function to return a csv line of all sensehat data
def get_sensehat_data():
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

    # return output data
    return output_data

# define starting time for thread completion
start_time = time()

# log script start
events_logger.info('Started logging')

while time() < start_time + timeout:
    # take sensor measurements every second within the picamera logging interval
    for second in range(1, picamera_capture_interval):
        sleep(1)
        sensor_logger.info(','.join(str(value) for value in get_sensehat_data()))
        
    with picamera.PiCamera() as camera:
        # set to maximum v2 resolution
        camera.resolution = (3280, 2464)
        
        # let automatic exposure settle for 2 seconds
        sleep(1)
        sensor_logger.info(','.join(str(value) for value in get_sensehat_data()))
        sleep(1)

        # capture PNG image after processing
        image_name = os.path.join(log_dir, 'image_' + str(int(time())) + '.png')
        camera.capture(image_name)
        images_logger.info(image_name)

        # capture unencoded RGB directly to binary file
        image_name = os.path.join(log_dir, 'rgb_' + str(int(time())) + '.data')
        with open(image_name, 'wb') as binary_file:
            camera.capture(binary_file, 'rgb')
        
        # log image save
        images_logger.info(image_name)

        # capture Bayer data to binary file after demosaicing
        image_name = os.path.join(log_dir, 'rgb_bayer_' + str(int(time())) + '.data')
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

# log script completion
events_logger.info('Finished logging')
