## http://picamera.readthedocs.io/en/release-1.10/recipes2.html#bayer-data

import time
import picamera
import picamera.array

with picamera.PiCamera() as camera:
    with picamera.array.PiBayerArray(camera) as stream:
        camera.capture(stream, 'jpeg', bayer=True)
        # Demosaic data and write to output (just use stream.array if you
        # want to skip the demosaic step)
        output = (stream.demosaic() >> 2).astype(numpy.uint8)
        with open('bayer.data', 'wb') as output_file:
            output.tofile(output_file)
