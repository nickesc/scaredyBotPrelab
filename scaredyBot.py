#!/usr/bin/env python3

import sensors as piSensors
from pycreate2 import Create2
import time
import RPi.GPIO as GPIO


class ScaredyBot():

    baseSpeed = 100

    def __init__(self, tty):
        self.botPort = tty  # where is your serial port?
        self.bot = Create2(self.botPort)
        self.state = {'bot': self.bot.get_sensors(), 'pi': piSensors}
        self.setState()

    # driving the bot - speed between 0 & 3; direction is 'forward' or 'back'
    def drive(self, speed = 1, dir = 'forward'):
        return

    def driveOne(self, speed = 1, dir = 'forward'):
        return

    def rotate(self, direction, degrees = 90):
        return

    def checkAround(self):
        return

    def runAway(self):
        return

    def setState(self):
        try:
            self.state = {'bot': self.bot.get_sensors(), 'pi': piSensors}
            return True
        except:
            return False

    def getSensors(self):
        self.setState()
        return self.state

    def checkMotion(self):
        return self.getSensors()['pi']['motion']


def loop():
    global scaredyBot
    print(scaredyBot.getSensors())
    time.sleep(.1)
    scaredyBot.checkMotion()
    time.sleep(.1)

def destroy():
    print("Quitting")
    GPIO.cleanup()

if __name__ == '__main__':

    scaredyBot = ScaredyBot('/dev/ttyUSB0')

    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()

