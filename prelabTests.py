from pycreate2 import Create2
import pyfirmata
import serial
import time

botPort = "/dev/tty.usbserial-DN026A6A"  # where is your serial port?
boardPort = "/dev/tty.usbmodem1101"

#bot = Create2(botPort)

#firmataBoard = pyfirmata.Arduino(boardPort)
serialBoard = serial.Serial(boardPort, 9600)

def serialTest(board):
    while(True):
        num = input("Enter a number: ")  # Taking input from user
        value = serialWrite(board,num)
        print(value)

def serialWrite(board,x):

    board.write(bytes(x, 'utf-8'))
    time.sleep(0.05)
    data = board.readline()
    return data

def botTest(bot):
    bot.start()
    bot.safe()
    bot.drive_direct(100, 100)
    time.sleep(2)
    bot.drive_direct(200, -200)  # inputs for motors are +/- 500 max
    time.sleep(2)
    bot.drive_stop()
    sensors = bot.get_sensors()  # returns all data
    print(sensors.light_bumper_left)

def firmataTest(board):
    while True:
        board.digital[13].write(1)
        time.sleep(1)
        board.digital[13].write(0)
        time.sleep(1)


if __name__ == '__main__':
    #botTest(bot)
    #firmataTest(firmataBoard)
    serialTest(serialBoard)