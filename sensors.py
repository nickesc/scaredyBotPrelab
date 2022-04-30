#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time

ObstaclePin = 17
pirPin = 27  # the pir connect to pin17


def setup():
    GPIO.setmode(GPIO.BCM)  # Set the GPIO modes to BCM Numbering
    GPIO.setup(pirPin, GPIO.IN)  # Set pirPin to input
    GPIO.setup(ObstaclePin, GPIO.IN, pull_up_down = GPIO.PUD_UP)



def MAP(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min



def loop():
    while True:

        pir_val = GPIO.input(pirPin)
        print(pir_val)

        if (0 == GPIO.input(ObstaclePin)):
            print("Detected Barrier!")
            time.sleep(1)



def destroy():

    GPIO.cleanup()  # Release resource


if __name__ == '__main__':  # Program start from here
    setup()
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()

