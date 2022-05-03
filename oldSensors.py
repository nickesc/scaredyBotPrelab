#!/usr/bin/env python3


import RPi.GPIO as GPIO
import time

obstaclePin = 17 # obstacle module pin = GPIO17 (BCM) / 11 (board)
pirPin = 27  # PIR motion pin = GPIO27 (BCM) / 13 (board)
trigPin = 23 # ultrasonic module trig pin = GPIO23 (BCM) / 16 (board)
echoPin = 24 # ultrasonic module echo pin = GPIO24 (BCM) / 18 (board)



def setup():
    GPIO.setmode(GPIO.BCM)  # Set the GPIO modes to BCM Numbering

    GPIO.setup(pirPin, GPIO.IN)
    GPIO.setup(obstaclePin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(trigPin, GPIO.OUT)
    GPIO.setup(echoPin, GPIO.IN)


def distance():
    GPIO.output(trigPin, 0)
    time.sleep(0.000002)

    GPIO.output(trigPin, 1)
    time.sleep(0.00001)
    GPIO.output(trigPin, 0)

    while GPIO.input(echoPin) == 0:
        a = 0
    time1 = time.time()
    while GPIO.input(echoPin) == 1:
        a = 1
    time2 = time.time()

    during = time2 - time1
    return during * 340 / 2 * 100

def MAP(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min



def loop():
    while True:

        dis = distance()
        print('Distance: %.2f' % dis)

        pir_val = GPIO.input(pirPin)
        print("Motion:",pir_val)

        print("Barrier:", GPIO.input(obstaclePin))
        time.sleep(.02)



def destroy():

    GPIO.cleanup()  # Release resource


if __name__ == '__main__':  # Program start from here
    setup()
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()

