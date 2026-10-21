from pybricks.ev3devices import TouchSensor, ColorSensor, UltrasonicSensor, GyroSensor
from pybricks.parameters import Port, Color
 
# change port for sensor as needed
touchSensor = TouchSensor(Port.S1)  
# colorSensor = ColorSensor(Port.?)
# ultrasonicSensor = UltrasonicSensor(Port.?)
# gyroSensor = GyroSensor(Port.?)

 
def isTouched():
    return touchSensor.is_pressed()

# def isRedTape();
    # return colorSensor.color() == Color.RED

# def isBlueTape();
    # return colorSensor.color() == Color.BLUE

# def getDistance():
    # return ultrasonicSensor.distance()

# def isNearObstacle(threshold_mm=200):
    # return ultrasonicSensor.distance() < threshold_mm

# def getAngle():
    # return gyroSensor.angle()

# def hasTurnedDegrees(target_angle):
    # return abs(gyroSensorangle()) >= abs(taraget_angle)

# def resetHeading():
    # gyroSensor.reset_angle(0)