#sample main.py for testing Microphyton for ESP32 for Sparkfun TB6612FNG Motor Drive for two motors
from machine import Pin, PWM
from time import sleep
from TB6612FNG import Motor

import config

frequency = 50

PWMB = 15
BIN2 = 2
BIN1 = 0
STBY = 4
AIN1 = 16
AIN2 = 17
PWMA = 5

ofsetA = 1
ofsetB = 1


motor = Motor(BIN2,BIN1,STBY,AIN1,AIN2,PWMA,PWMB,ofsetA,ofsetB)


def start():
    for _ in range(3):
        motor.forward(500)
        sleep(6)

        motor.right(450)
        sleep(1.70)

        motor.forward(500)
        sleep(1.4)

        motor.right(450)
        sleep(1.70)

        motor.forward(500)
        sleep(6)

        motor.right(450)
        sleep(1.70)

        motor.forward(500)
        sleep(1.4)
        motor.right(450)
        sleep(1.70)

    motor.brake()
    motor.stop()
    motor.standby()

    
if __name__ == '__main__':
    start()






