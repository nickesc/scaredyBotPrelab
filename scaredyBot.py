#!/usr/bin/env python3

import sensors as piSensors
from pycreate2 import Create2
import time
import RPi.GPIO as GPIO


port = '/dev/ttyUSB0'

class ScaredyBot():

    baseSpeed = 100

    def __init__(self, tty):
        self.botPort = tty  # where is your serial port?
        self.bot = Create2(self.botPort)

        self.bot.start()
        self.bot.safe()

        self.state = {'bot': self.bot.get_sensors(), 'pi': piSensors.getSensors()}
        self.setState()

    def stop(self):
        self.bot.drive_stop()

    # driving the bot - speed between 0 & 3; direction is 'forward' or 'back'
    def drive(self, speed = 1, dir = 'forward'):
        return

    def driveUntilYouHitAWall(self, speed, direction = 'forward'):
        speed=speed*self.baseSpeed

        if direction=="back":
            speed = speed*-1

        self.bot.drive_direct(speed, speed)
        noWall = True
        while noWall:
            sensors = self.bot.get_sensors()
            bump = sensors.light_bumper
            if bump.front_left or bump.front_right:
                self.bot.drive_stop()
                noWall = False

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
            self.state = {'bot': self.bot.get_sensors(), 'pi': piSensors.getSensors()}
            return True
        except:
            return False

    def getSensors(self):
        self.setState()
        return self.state

    def checkMotion(self):
        return piSensors.getMotion()


def loop():
    global scaredyBot

    while True:
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
        print(scaredyBot.getSensors())
        time.sleep(.1)
        scaredyBot.driveUntilYouHitAWall(1)
        #bot = Create2(port)
        #print(bot.get_sensors())
        #scaredyBot.start()
        #loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()

