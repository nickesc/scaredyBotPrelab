#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import csv
import smbus
import math

obstaclePin = 17  # obstacle module pin = GPIO17 (BCM) / 11 (board)
pirPin = 27  # PIR motion pin = GPIO27 (BCM) / 13 (board)
trigPin = 23  # ultrasonic module trig pin = GPIO23 (BCM) / 16 (board)
echoPin = 24  # ultrasonic module echo pin = GPIO24 (BCM) / 18 (board)

# trigBack = 20
# echoBack = 16


outLogName = 'outlog.csv'
# fields = ['disFront', 'disBack', 'pirVal', 'obstacle']
fields = ['motion', 'gyro']


outLog = open(outLogName, 'a+')
writer = csv.DictWriter(outLog, fieldnames = fields)

currPhase = ['']
phases = []

power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c

bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards
address = 0x68       # This is the address value read via the i2cdetect command

def read_byte(adr):
    return bus.read_byte_data(address, adr)

def read_word(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr+1)
    val = (high << 8) + low
    return val

def read_word_2c(adr):
    val = read_word(adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def dist(a,b):
    return math.sqrt((a*a)+(b*b))

def get_y_rotation(x,y,z):
    radians = math.atan2(x, dist(y,z))
    return -math.degrees(radians)

def get_x_rotation(x,y,z):
    radians = math.atan2(y, dist(x,z))
    return math.degrees(radians)

def getGyro():

    gyro = {}

    gyro["gyro_xout"] = read_word_2c(0x43)
    gyro["gyro_yout"] = read_word_2c(0x45)
    gyro["gyro_zout"] = read_word_2c(0x47)

    gyro["gyro_xout_scaled"] = gyro["gyro_xout"] / 131
    gyro["gyro_yout_scaled"] = gyro["gyro_yout"] / 131
    gyro["gyro_zout_scaled"] = gyro["gyro_zout"] / 131

    gyro["accel_xout"] = read_word_2c(0x3b)
    gyro["accel_yout"] = read_word_2c(0x3d)
    gyro["accel_zout"] = read_word_2c(0x3f)

    gyro["accel_xout_scaled"] = gyro["accel_xout"] / 16384.0
    gyro["accel_yout_scaled"] = gyro["accel_yout"] / 16384.0
    gyro["accel_zout_scaled"] = gyro["accel_zout"] / 16384.0

    gyro["x_rotation"] = get_x_rotation(["accel_xout_scaled"], ["accel_yout_scaled"], ["accel_zout_scaled"])
    gyro["y_rotation"] = get_y_rotation(["accel_xout_scaled"], ["accel_yout_scaled"], ["accel_zout_scaled"])

def logPhase(phase, full = False):
    currPhase[0] = phase
    phases.append(phase)

    if (full == True):
        print(phases)


def clearLog():
    logPhase('clearLog')
    outLog.truncate(0)
    writer.writeheader()


def setup():
    logPhase('setup')

    clearLog()

    GPIO.setmode(GPIO.BCM)  # Set the GPIO modes to BCM Numbering

    GPIO.setup(pirPin, GPIO.IN)

    # Now wake the 6050 up as it starts in sleep mode
    bus.write_byte_data(address, power_mgmt_1, 0)
    # GPIO.setup(obstaclePin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    # GPIO.setup(trigFront, GPIO.OUT)
    # GPIO.setup(echoFront, GPIO.IN)
    # GPIO.setup(trigBack, GPIO.OUT)
    # GPIO.setup(echoBack, GPIO.IN)


def getDist(sensor):
    logPhase('distFront')
    global trigFront, echoFront, trigBack, echoBack  # Allow access to 'trig' and 'echo' constants

    if (sensor == 'front'):
        if GPIO.input(echoFront):  # If the 'Echo' pin is already high
            return 100.000  # then exit with 100 (sensor fault)
    elif (sensor == 'back'):
        if GPIO.input(echoBack):  # If the 'Echo' pin is already high
            return 100.000  # then exit with 100 (sensor fault)
    else:
        raise Exception('invalid distance sensor')

    distance = 0  # Set initial distance to zero

    if (sensor == 'front'):
        GPIO.output(trigFront, False)  # Ensure the 'Trig' pin is low for at
    elif (sensor == 'back'):
        GPIO.output(trigBack, False)  # Ensure the 'Trig' pin is low for at
    else:
        raise Exception('invalid distance sensor')

    time.sleep(0.05)  # least 50mS (recommended re-sample time)

    if (sensor == 'front'):
        GPIO.output(trigFront, True)  # Turn on the 'Trig' pin for 10uS (ish!)
    elif (sensor == 'back'):
        GPIO.output(trigBack, True)  # Turn on the 'Trig' pin for 10uS (ish!)
    else:
        raise Exception('invalid distance sensor')

    dummy_variable = 0  # No need to use the 'time' module here,
    dummy_variable = 0  # a couple of 'dummy' statements will do fine

    if (sensor == 'front'):
        GPIO.output(trigFront, False)  # Turn off the 'Trig' pin
    elif (sensor == 'back'):
        GPIO.output(trigBack, False)  # Turn off the 'Trig' pin
    else:
        raise Exception('invalid distance sensor')

    time1, time2 = time.time(), time.time()  # Set inital time values to current time

    if (sensor == 'front'):
        while not GPIO.input(echoFront):  # Wait for the start of the 'Echo' pulse
            time1 = time.time()  # Get the time the 'Echo' pin goes high
            if time1 - time2 > 0.02:  # If the 'Echo' pin doesn't go high after 20mS
                distance = 100  # then set 'distance' to 100
                break  # and break out of the loop
    elif (sensor == 'back'):
        while not GPIO.input(echoBack):  # Wait for the start of the 'Echo' pulse
            time1 = time.time()  # Get the time the 'Echo' pin goes high
            if time1 - time2 > 0.02:  # If the 'Echo' pin doesn't go high after 20mS
                distance = 100  # then set 'distance' to 100
                break  # and break out of the loop
    else:
        raise Exception('invalid distance sensor')

    if distance == 100:  # If a sensor error has occurred
        return format(distance, '.2f')  # then exit with 100 (sensor fault)

    if (sensor == 'front'):
        while GPIO.input(echoFront):  # Otherwise, wait for the 'Echo' pin to go low
            time2 = time.time()  # Get the time the 'Echo' pin goes low
            if time2 - time1 > 0.02:  # If the 'Echo' pin doesn't go low after 20mS
                distance = 100  # then ignore it and set 'distance' to 100
                break  # and break out of the loop
    elif (sensor == 'back'):
        while GPIO.input(echoBack):  # Otherwise, wait for the 'Echo' pin to go low
            time2 = time.time()  # Get the time the 'Echo' pin goes low
            if time2 - time1 > 0.02:  # If the 'Echo' pin doesn't go low after 20mS
                distance = 100  # then ignore it and set 'distance' to 100
                break  # and break out of the loop
    else:
        raise Exception('invalid distance sensor')

    if distance == 100:  # If a sensor error has occurred
        return format(distance, '.2f')  # then exit with 100 (sensor fault)

        # Sound travels at approximately 2.95uS per mm
        # and the reflected sound has travelled twice
        # the distance we need to measure (sound out,
        # bounced off object, sound returned)

    distance = (time2 - time1) / 0.00000295 / 2 / 10  # Convert the timer values into centimetres
    return format(distance, '.2f')  # Exit with the distance in centimetres


def getMotion(maxSample = 10):
    logPhase('motion')

    if (GPIO.input(pirPin) == 0):
        return False
    else:
        return True


def getObstacle():
    logPhase('obstacle')

    if (GPIO.input(obstaclePin) == 1):
        return False
    else:
        return True


def getSensors(output = False):
    # distFront = getDist('front')
    # distBack = getDist('back')

    motion = getMotion()

    gyro = getGyro()

    # obstacle = getObstacle()
    logPhase('collectedData')

    # data = {'disFront': distFront, 'disBack': distBack, 'pirVal': motion, 'obstacle': obstacle}

    data = {'motion': motion, 'gyro':gyro}

    writer.writerow(data)
    logPhase('wroteData')
    if (output):
        # print("{: >10} {: >10} {: >10} {: >10}".format(*[distFront, distBack, motion, obstacle]))
        print("Motion:", motion)
        print("Gyro:", gyro)

    return (data)


def loop():
    logPhase('loopStart')
    while True:
        getSensors(output = True)
        time.sleep(.3)


def destroy():
    outLog.close()
    GPIO.cleanup()  # Release resource

    logPhase('destroy')


setup()

if __name__ == '__main__':  # Program start from here
    logPhase('start')

    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()
