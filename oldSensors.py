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

phaseLogName = 'phases.log'
outLogName = 'outlog.csv'
fields = ['disFront', 'disBack', 'pirVal', 'obstacle']

phaseLog = open(phaseLogName, 'a+')
outLog = open(outLogName, 'a+')
writer = csv.DictWriter(outLog,fieldnames = fields)


currPhase = ['']
phases = []

motion=[0]*(100)
motionIndex = 0


def logPhase(phase, full = False):
    currPhase[0]=phase
    phases.append(phase)

    if(full == True):
        print(phases)

def clearLog():
    logPhase('clearLog')
    phaseLog.truncate(0)
    outLog.truncate(0)
    writer.writeheader()

def setup():
    logPhase('setup')

    clearLog()

    GPIO.setmode(GPIO.BCM)  # Set the GPIO modes to BCM Numbering

    GPIO.setup(pirPin, GPIO.IN)
    GPIO.setup(obstaclePin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(trigFront, GPIO.OUT)
    GPIO.setup(echoFront, GPIO.IN)
    GPIO.setup(trigBack, GPIO.OUT)
    GPIO.setup(echoBack, GPIO.IN)

def getBack():
    logPhase('distBack')
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
    logPhase('distFront')
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

def getMotion():
    global motion

    logPhase('motion')

    motion.pop()
    motion = [GPIO.input(pirPin)] + motion

    if (motion.count(0)>50):
        return False
    else:
        return True

def getObstacle():
    logPhase('obstacle')
    if (GPIO.input(obstaclePin) == 1):
        return False
    else:
        return True

def MAP(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def loop():
    logPhase('loopStart')
    while True:
        distFront = getFront()
        distBack = getBack()
        pirVal = getMotion()
        obstacle = getObstacle()
        logPhase('collectedData')

        data = {'disFront': distFront, 'disBack': distBack, 'pirVal': pirVal, 'obstacle': obstacle}

        writer.writerow(data)

        logPhase('wroteData')

        print(data)


def destroy():
    outLog.close()
    GPIO.cleanup()  # Release resource

    logPhase('destroy')


if __name__ == '__main__':  # Program start from here
    logPhase('start')
    setup()
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()
