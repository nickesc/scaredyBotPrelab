#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import csv

obstaclePin = 17 # obstacle module pin = GPIO17 (BCM) / 11 (board)
pirPin = 27  # PIR motion pin = GPIO27 (BCM) / 13 (board)
trigFront = 23 # ultrasonic module trig pin = GPIO23 (BCM) / 16 (board)
echoFront = 24 # ultrasonic module echo pin = GPIO24 (BCM) / 18 (board)

trigBack = 20
echoBack = 16

outLog = 'outlog.csv'
fields = ['disFront', 'disBack', 'pirVal', 'obstacle']

with open(outLog, 'w') as log:
    log.write("")

def setup():
    GPIO.setmode(GPIO.BCM)  # Set the GPIO modes to BCM Numbering

    GPIO.setup(pirPin, GPIO.IN)
    GPIO.setup(obstaclePin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(trigFront, GPIO.OUT)
    GPIO.setup(echoFront, GPIO.IN)
    GPIO.setup(trigBack, GPIO.OUT)
    GPIO.setup(echoBack, GPIO.IN)


def distance(sensor):

    if (sensor == 'front'):
        trig = trigFront
        echo = echoFront
    else:
        trig = trigBack
        echo = echoBack

    GPIO.output(trig, 0)
    time.sleep(0.000002)

    GPIO.output(trig, 1)
    time.sleep(0.00001)
    GPIO.output(trig, 0)

    while GPIO.input(echo) == 0:
        a = 0
    time1 = time.time()
    while GPIO.input(echo) == 1:
        a = 1
    time2 = time.time()

    during = time2 - time1
    return during * 340 / 2 * 100

def MAP(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min



def loop(writer):
    while True:
        disFront = distance('front')
        disBack = distance('back')
        pirVal = GPIO.input(pirPin)
        obstacle = GPIO.input(obstaclePin)

        data = {'disFront': disFront, 'disBack': disBack, 'pirVal': pirVal, 'obstacle': obstacle}
        writer.writerow(data)

        time.sleep(.5)

def destroy():

    GPIO.cleanup()  # Release resource


if __name__ == '__main__':  # Program start from here
    setup()

    try:
        with open(outLog, 'a') as log:
            writer = csv.DictWriter(log, fieldnames = fields)
            writer.writeheader()
            loop(writer)
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()

