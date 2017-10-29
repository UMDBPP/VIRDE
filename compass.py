#!/usr/bin/python
import sys
import math
from sense_hat import SenseHat

# To get good results with the magnetometer you must first calibrate it using
# the program in RTIMULib/Linux/RTIMULibCal
# The calibration program will produce the file RTIMULib.ini
# Copy it into the same folder as your Python code

led_loop = [4, 5, 6, 7, 15, 23, 31, 39, 47, 55, 63, 62, 61, 60, 59, 58, 57, 56, 48, 40, 32, 24, 16, 8, 0, 1, 2, 3]

sense = SenseHat()
sense.set_rotation(0)
sense.clear()

prev_x = 0
prev_y = 0

led_degree_ratio = len(led_loop) / 360.0

while True:
    dir = sense.get_compass()
    dir_inverted = 360 - dir  # So LED appears to follow North
    led_index = int(led_degree_ratio * dir_inverted)
    offset = led_loop[led_index]
    
    y = offset // 8  # row
    x = offset % 8  # column

    if x != prev_x or y != prev_y:
        sense.set_pixel(prev_x, prev_y, 0, 0, 0)

    sense.set_pixel(x, y, 0, 0, 255)

    prev_x = x
    prev_y = y
    
    magnetometer = sense.get_compass_raw()
    orientation = sense.get_orientation()
    
    mag_x = magnetometer['x']
    mag_y = magnetometer['y']
    mag_z = magnetometer['z']
    
    yaw = orientation['yaw']
    pitch = orientation['pitch']
    roll = orientation['roll']
    
    X_h = mag_x * math.cos(pitch) + mag_y * math.sin(roll) * math.sin(pitch) - mag_z * math.cos(roll) * math.sin(pitch)

    Y_h = mag_y * math.cos(roll) - mag_z * math.sin(roll)

    heading = math.atan2(Y_h, X_h) * 180 / math.pi  #+ 180
    
    print("raw_imu: " + str(yaw) + " " + str(pitch) + " " + str(roll))
    print("raw_mag: " + str(mag_x) + " " + str(mag_y) + " " + str(mag_z))
    print("heading: " + str(heading))
    print("compass: " + str(dir) + " " + str(dir_inverted))
