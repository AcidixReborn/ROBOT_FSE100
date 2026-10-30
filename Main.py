#!/usr/bin/env pybricks-micropython
# main.py
import socket

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor, ColorSensor, UltrasonicSensor, GyroSensor
from pybricks.parameters import Port, Color 
from pybricks.robotics import DriveBase
from pybricks.tools import wait


# Initialize EV3 components
ev3 = EV3Brick()
left_motor = Motor(Port.A)
right_motor = Motor(Port.D)
# weapon = Motor(Port.A)
robot = DriveBase(left_motor, right_motor, wheel_diameter=55.5, axle_track=104)

# Touch Sensor Initialization
touchSensor = TouchSensor(Port.S2)

# Color Sensor Initialization
colorSensor = ColorSensor(Port.S3)
onTape = False

# Color RGB Reference Values...INITIAL SETUP REQUIRED 
colorReferences = {
    "RED": (0, 0, 0),
    "GREEN": (0, 0, 0),
    "BLUE": (0, 0, 0),
    "YELLOW": (0, 0, 0),
    "FLOOR": (0, 0, 0)
}

# Stop Colors: Pick which colors to stop on based on which ones end up being the pickup and dropoff locations...DISABLED UNTIL TESTING IS DONE
stopColors = [
    "RED",
    "GREEN",
    "BLUE",
    "YELLOW"
]

# Max Diff of Color RGB
maxDiff = 30

# Gyro Sensor Initialization
gyroSensor = GyroSensor(Port.S1)
gyroSensor.reset_angle(0)
lastAngle = None    

# Ultrasonic Sensor Initialization
ultrasonicSensor = UltrasonicSensor(Port.S4)
lastDistance = None

# Autonomous Mode Initialization
autoMode = False
targetDistance = 340

# Server configuration
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 12345))
server_socket.listen(1)
print("Waiting for connection...")
client_socket, address = server_socket.accept()
print("Connected to {}".format(address))

#  added setBlocking so that the Color Sensor and UltraSonic Searches all the time.
client_socket.setblocking(False)

def playTune(num):
    if num == 0:
        ev3.speaker.beep(frequency=440, duration=340)
        ev3.speaker.beep(frequency=329, duration=170)
        ev3.speaker.beep(frequency=349, duration=170)
        ev3.speaker.beep(frequency=392, duration=170)
        ev3.speaker.beep(frequency=440, duration=85) 
        ev3.speaker.beep(frequency=392, duration=85)
        ev3.speaker.beep(frequency=349, duration=170)
        ev3.speaker.beep(frequency=329, duration=170)
        ev3.speaker.beep(frequency=293, duration=255)
        wait(85)
        ev3.speaker.beep(frequency=293, duration=170)
        ev3.speaker.beep(frequency=349, duration=170)
        ev3.speaker.beep(frequency=440, duration=340)
        ev3.speaker.beep(frequency=392, duration=170)
        ev3.speaker.beep(frequency=349, duration=170)
        ev3.speaker.beep(frequency=329, duration=510)
        ev3.speaker.beep(frequency=349, duration=170)
        ev3.speaker.beep(frequency=392, duration=340)
        ev3.speaker.beep(frequency=440, duration=340)
        ev3.speaker.beep(frequency=349, duration=340)
        ev3.speaker.beep(frequency=293, duration=85)
        wait(255)
        ev3.speaker.beep(frequency=293, duration=340)

try:
    
    while True:

        # Touch Sensor Enabled
        if touchSensor.pressed():
            autoMode = False
            robot.stop()
            ev3.speaker.beep(frequency=440, duration=100)
        
        # Color Sensor Enabled...MORE TESTING REQUIRED

        r, g, b = colorSensor.rgb()
        currentColor = None
        closestDiff = None
        for name in colorReferences:
            refR, refG, refB = colorReferences[name]
            diff = abs(r - refR) + abs(g - refG) + abs(b - refB)
            if closestDiff is None or diff < closestDiff:
                closestDiff = diff
                currentColor = name

        if closestDiff > maxDiff:
            currentColor = None

        if currentColor in stopColors:
            if not onTape:
                onTape = True
                robot.stop()
                ev3.screen.clear()
                ev3.screen.print(currentColor)
                ev3.speaker.beep(frequency=440, duration=100)
                wait(5000)
                try:
                    while client_socket.recv(2):
                        pass
                except OSError:
                    pass
                # ev3.speaker.beep(frequency=440, duration=100)
        else:
            onTape = False

        # Gyro Sensor Enabled
        currentAngle = gyroSensor.angle()
        # if currentAngle != lastAngle:
        #     ev3.screen.clear()
        #     ev3.screen.print(currentAngle)
        #     lastAngle = currentAngle

        # Ultrasonic Sensor Enabled
        currentDistance = ultrasonicSensor.distance()
        # if currentDistance != lastDistance:
        #     ev3.screen.clear()
        #     ev3.screen.print(currentDistance)
        #     lastDistance = currentDistance

        if autoMode:
            distance = ultrasonicSensor.distance()
            distanceToGo = distance - targetDistance
            if abs(distanceToGo) <= 10:
                robot.stop()
                targetAngle = currentAngle - 90
                while (abs(targetAngle - gyroSensor.angle()) > 3):
                    robot.drive(0, 90)
                robot.stop()
                autoMode = False
                playTune(0)
            else:  
                speed = distanceToGo * 2
                speed = max(-300, min(300, speed))
                robot.drive(speed, 0)

        try: 
            command = client_socket.recv(2).decode()
        # added except so that the program doesnt break if no input is recieved (key movements)
        except OSError:
            wait(10)
            continue
        if not command:
            break
        
        # Keyboard Commands for Movement
        key, action = command[0], command[1]

        
        # AutoMode Stops WASD and Weapon Input...TESTING REQUIRED
        if key == " ":
            if action == "d":
                autoMode = not autoMode
                robot.stop()
            continue

        if autoMode:
            continue

        if action == "d":  # Key press
            if key == "w":
                robot.drive(900, 0)  # Move forward
            elif key == "s":
                robot.drive(-900, 0)  # Move backward
            elif key == "a":
                robot.drive(0, -450)  # Turn left
            elif key == "d":
                robot.drive(0, 450)  # Turn right
            #elif key == "f":
            #    weapon.run(1000)  # Spin weapon motor at max speed
        elif action == "u":  # Key release
            if key in ("w", "a", "s", "d"):
                robot.stop()  # Stop the robot on key release
            #elif key == "f":
            #    weapon.stop()  # Stop the weapon motor on key release


finally:
    client_socket.close()
    server_socket.close()
