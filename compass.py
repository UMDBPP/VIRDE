#!/usr/bin/python
import sys
import math

from sense_hat import SenseHat
import gps
 
# Listen on port 2947 (gpsd) of localhost
session = gps.gps("localhost", "2947")
session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
 
# To get good results with the magnetometer you must first calibrate it using
# the program in RTIMULib/Linux/RTIMULibCal
# The calibration program will produce the file RTIMULib.ini
# Copy it into the same folder as your Python code

sense = SenseHat()

prev_x = 0
prev_y = 0

while True:
    compass_dir = 360 - sense.get_compass()
    
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
    
    print("raw_imu: %d %d %d" % (yaw, pitch, roll))
    print("raw_mag: %d %d %d" % (mag_x, mag_y, mag_z))
    print("%d %d %d" % (compass_dir, heading, compass_dir - heading))
    
    try:
        report = session.next()
        # Wait for a 'TPV' report and display the current time
        # To see all report data, uncomment the line below
        # print report
        if report['class'] == 'TPV':
            if hasattr(report, 'time'):
                print report.time
    except KeyError:
        pass
    except KeyboardInterrupt:
        quit()
    except StopIteration:
        session = None
        print "GPSD has terminated"
