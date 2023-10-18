#sample main.py for testing Microphyton for ESP32 for Sparkfun TB6612FNG Motor Drive for two motors
from machine import Pin, PWM
from time import sleep
from TB6612FNG import Motor

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


#print("moving forward")
#motor.right(800)
#sleep(60)

print("moving forward")
motor.forward(500)
sleep(5)

print("moving backward")
motor.right(800)
sleep(2.5)

#print("moving forward")
#motor.forward(500)
#sleep(10)

#print("moving right")
#motor.right(500)
#sleep(4)

#print("moving forward")
#motor.forward(500)
#sleep(10)

#print("moving right")
#motor.right(500)
#sleep(4)

#print("moving forward")
#motor.forward(500)
#sleep(10)

#motor.backward(600)
#sleep(10)

#print("moving right")
#motor.right(700)
#sleep(10)

#motor.left(800)
#sleep(10)

motor.brake()
sleep(5)

motor.stop()
sleep(5)

motor.standby()
sleep(5)

motor.run()
sleep(5)




