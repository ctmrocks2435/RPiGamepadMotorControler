#######################################################
# RaspberryPI RC control software.
# Desined to take gamepad input and transmit via
# Serial to a Sabertooth MCU.
#
# Required pyserial and inputs. Use pip install for this.
# Requires raspberry-config be used to enable serial ports.
#
# Collin Matthews
# 20-AUG-2017
#######################################################
from inputs import get_gamepad
import serial
import time



SERIAL_PORT = "COM6"
SERIAL_BAUD = 9600
STICK_ZERO_THRESH = 3
STICK_ONE_THRESH = 62
motorL=0
motorR=0
SERIAL_DELAY = 50



    
"""Configure and start serial system."""
def serialConfig(spport,baud):
    global serialOut
    serialOut = serial.Serial(
               port=spport,
               baudrate = baud,
               parity=serial.PARITY_NONE,
               stopbits=serial.STOPBITS_ONE,
               bytesize=serial.EIGHTBITS,
               timeout=0,
               writeTimeout=1
           )
    


    
""" Sets motor speed via TTL SERIAL. 
    Send -1 - 1? for motor speed?"""
def setMotorSpeed(speed, side):
#Motor 1: 1=FullRev 64=Stop 127=FullFwd
#Motor 2: 128=FullRev 192=Stop 255=FullFwd
#Sending 0 will stop both motors.
    global serialOut
    #print("Lm:" + str(leftMotor) + " Rm:" + str(rightMotor))
    #SCALE FOR 8 BIT
    if side == 0:
        speed = int(speed) + 64
        if speed == 0: speed = 1 #Left has 1 less precision.
    else:
        speed = int(speed) + 192
    serialOut.write(speed)
    print("Side:" + str(side) + " Speed:" + str(speed))




"""Filter Inputs for only button/stick data.
    Outputs -64 to 63. (7 bit)"""
def inputFilter(event):
    #print(event.ev_type, event.code, event.state)
    if event.ev_type is not "Sync":
        eventcode = event.code
        data = event.state
        if eventcode in ('ABS_Y','ABS_RY'):
            data=round(data/512)
            #Force 0 on bad sticks.
            if data > -1*STICK_ZERO_THRESH and data < STICK_ZERO_THRESH: data=0
            if data > STICK_ONE_THRESH: data = 63
            if data < -1*STICK_ONE_THRESH: data = -64
            return str(eventcode) + "=" + str(data)




def main():
    global motorL
    global motorR
    
    #Start Serial
    global serialOut
    serialConfig(SERIAL_PORT, SERIAL_BAUD)

    #Set Motors to 0?
    
    #Start Control Loop.
    cnt_l=0
    sts=True
    eventTimer=0
    while 1:
        events = get_gamepad()
        for event in events:
            eventResult = inputFilter(event)
            if eventResult is not None:
                if eventResult.startswith("ABS_Y"):
                    t0=time.time()
                    if ((t0-eventTimer)*1000 > SERIAL_DELAY):
                        motorL=eventResult.split("=")[1]
                        setMotorSpeed(motorL,0)
                        eventTimer = time.time()
                        
                if eventResult.startswith("ABS_RY"):
                    if ((t0-eventTimer)*1000 > SERIAL_DELAY):
                        motorR=eventResult.split("=")[1]
                        eventTimer = time.time()
                        setMotorSpeed(motorR,1) 

                        
                        
        
if __name__ == "__main__":
    main()
    
    



    

    
    
    
    
    
    
    
    
    
    
    
    
    