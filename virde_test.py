# package imports
import os
from time import sleep, time, strftime
from datetime import datetime

# Raspberry Pi hardware imports
import picamera
import picamera.array

# free space is 24097.036 mB / 23.2 mB -> 988.226721517 images -> 900 images to be safe

# define camera capture interval
picamera_capture_interval = 20

# average flight time is 98.92 minutes, longest ever flight was 175.53 minutes
timeout_seconds = 60

# define path to log directory
log_dir = os.path.join('/home/pi/Desktop', 'virde_test_log', 'log_' + strftime("%Y%m%d_%H%M%S_%Z"))

# create path to log directory if it doesn't exist
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

# define starting time
start_time = time()

# note that camera takes about 13 seconds to initialize
with picamera.PiCamera() as camera:
    # set to maximum v2 resolution
    camera.resolution = (3280, 2464)
    
    # continue until timeout_seconds is exceeded
    while time() < start_time + timeout_seconds:
        current_start_time = time()
        
        # capture unencoded RGB directly to binary file
        image_name = os.path.join(log_dir, strftime("%Y%m%d_%H%M%S_%Z") + '_rgb_' + '.bip')
        with open(image_name, 'wb') as binary_file:
            camera.capture(binary_file, 'rgb')
            
        print("Image taken in " + str(time() - current_start_time) + "seconds")
        
        sleep(picamera_capture_interval)


