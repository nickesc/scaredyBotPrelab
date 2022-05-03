#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import csv

obstaclePin = 17  # obstacle module pin = GPIO17 (BCM) / 11 (board)
pirPin = 27  # PIR motion pin = GPIO27 (BCM) / 13 (board)
trigFront = 23  # ultrasonic module trig pin = GPIO23 (BCM) / 16 (board)
echoFront = 24  # ultrasonic module echo pin = GPIO24 (BCM) / 18 (board)

trigBack = 20
echoBack = 16

outLog = 'outlog.csv'
fields = ['disFront', 'disBack', 'pirVal', 'obstacle']

def microsecondsToInches(microseconds):
  return microseconds / 74 / 2


def microsecondsToCentimeters(microseconds):
  return microseconds / 29 / 2


def setup():
    GPIO.setmode(GPIO.BCM)  # Set the GPIO modes to BCM Numbering

    GPIO.setup(pirPin, GPIO.IN)
    GPIO.setup(obstaclePin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(trigFront, GPIO.OUT)
    GPIO.setup(echoFront, GPIO.IN)
    GPIO.setup(trigBack, GPIO.OUT)
    GPIO.setup(echoBack, GPIO.IN)


def distanceBack():
    GPIO.output(trigBack, 0)
    time.sleep(0.000002)

    GPIO.output(trigBack, 1)
    time.sleep(0.00001)
    GPIO.output(trigBack, 0)

    while GPIO.input(echoBack) == 0:
        a = 0
    time1 = time.time()
    while GPIO.input(echoBack) == 1:
        a = 1
    time2 = time.time()
    during = time2 - time1
    return during * 340 / 2 * 100


def distanceFront():
    GPIO.output(trigFront, 0)
    time.sleep(0.000002)

    GPIO.output(trigFront, 1)
    time.sleep(0.00001)
    GPIO.output(trigFront, 0)

    while GPIO.input(echoFront) == 0:
        a = 0
    time1 = time.time()
    while GPIO.input(echoFront) == 1:
        a = 1
    time2 = time.time()

    during = time2 - time1
    return during * 340 / 2 * 100

def getBack():
    global trigBack, echoBack  # Allow access to 'trig' and 'echo' constants

    if GPIO.input(echoBack):  # If the 'Echo' pin is already high
        return (100)  # then exit with 100 (sensor fault)

    distance = 0  # Set initial distance to zero

    GPIO.output(trigBack, False)  # Ensure the 'Trig' pin is low for at
    time.sleep(0.05)  # least 50mS (recommended re-sample time)

    GPIO.output(trigBack, True)  # Turn on the 'Trig' pin for 10uS (ish!)
    dummy_variable = 0  # No need to use the 'time' module here,
    dummy_variable = 0  # a couple of 'dummy' statements will do fine

    GPIO.output(trigBack, False)  # Turn off the 'Trig' pin
    time1, time2 = time.time(), time.time()  # Set inital time values to current time

    while not GPIO.input(echoBack):  # Wait for the start of the 'Echo' pulse
        time1 = time.time()  # Get the time the 'Echo' pin goes high
        if time1 - time2 > 0.02:  # If the 'Echo' pin doesn't go high after 20mS
            distance = 100  # then set 'distance' to 100
            break  # and break out of the loop

    if distance == 100:  # If a sensor error has occurred
        return (distance)  # then exit with 100 (sensor fault)

    while GPIO.input(echoBack):  # Otherwise, wait for the 'Echo' pin to go low
        time2 = time.time()  # Get the time the 'Echo' pin goes low
        if time2 - time1 > 0.02:  # If the 'Echo' pin doesn't go low after 20mS
            distance = 100  # then ignore it and set 'distance' to 100
            break  # and break out of the loop

    if distance == 100:  # If a sensor error has occurred
        return (distance)  # then exit with 100 (sensor fault)

        # Sound travels at approximately 2.95uS per mm
        # and the reflected sound has travelled twice
        # the distance we need to measure (sound out,
        # bounced off object, sound returned)

    distance = (time2 - time1) / 0.00000295 / 2 / 10  # Convert the timer values into centimetres
    return (distance)  # Exit with the distance in centimetres

def getFront():
    global trigFront, echoFront  # Allow access to 'trig' and 'echo' constants

    if GPIO.input(echoFront):  # If the 'Echo' pin is already high
        return (100)  # then exit with 100 (sensor fault)

    distance = 0  # Set initial distance to zero

    GPIO.output(trigFront, False)  # Ensure the 'Trig' pin is low for at
    time.sleep(0.05)  # least 50mS (recommended re-sample time)

    GPIO.output(trigFront, True)  # Turn on the 'Trig' pin for 10uS (ish!)
    dummy_variable = 0  # No need to use the 'time' module here,
    dummy_variable = 0  # a couple of 'dummy' statements will do fine

    GPIO.output(trigFront, False)  # Turn off the 'Trig' pin
    time1, time2 = time.time(), time.time()  # Set inital time values to current time

    while not GPIO.input(echoFront):  # Wait for the start of the 'Echo' pulse
        time1 = time.time()  # Get the time the 'Echo' pin goes high
        if time1 - time2 > 0.02:  # If the 'Echo' pin doesn't go high after 20mS
            distance = 100  # then set 'distance' to 100
            break  # and break out of the loop

    if distance == 100:  # If a sensor error has occurred
        return (distance)  # then exit with 100 (sensor fault)

    while GPIO.input(echoFront):  # Otherwise, wait for the 'Echo' pin to go low
        time2 = time.time()  # Get the time the 'Echo' pin goes low
        if time2 - time1 > 0.02:  # If the 'Echo' pin doesn't go low after 20mS
            distance = 100  # then ignore it and set 'distance' to 100
            break  # and break out of the loop

    if distance == 100:  # If a sensor error has occurred
        return (distance)  # then exit with 100 (sensor fault)

        # Sound travels at approximately 2.95uS per mm
        # and the reflected sound has travelled twice
        # the distance we need to measure (sound out,
        # bounced off object, sound returned)

    distance = (time2 - time1) / 0.00000295 / 2 / 10  # Convert the timer values into centimetres
    return (distance)  # Exit with the distance in centimetres

def MAP(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def loop():
    while True:
        disFront = getFront()
        disBack = getBack()
        pirVal = GPIO.input(pirPin)
        obstacle = GPIO.input(obstaclePin)

        data = {'disFront': disFront, 'disBack': disBack, 'pirVal': pirVal, 'obstacle': obstacle}

        print(data)


def destroy():
    GPIO.cleanup()  # Release resource


if __name__ == '__main__':  # Program start from here
    setup()
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()
