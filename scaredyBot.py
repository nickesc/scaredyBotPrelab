from sensors import *

if __name__ == '__main__':
    while True:
        print(getMotion())
        getSensors(output = True)

