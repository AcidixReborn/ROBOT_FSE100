from pybricks.ev3devices import TouchSensor
from pybricks.parameters import Port
 
# change port for sensor is needed
touchSensor = TouchSensor(Port.B)  
 
 
def isTouched():
    return touchSensor.pressed()
 