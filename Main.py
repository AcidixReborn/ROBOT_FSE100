#!/usr/bin/env pybricks-micropython
# main.py
import socket

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor, ColorSensor, UltrasonicSensor, GyroSensor
from pybricks.parameters import Port, Color 
from pybricks.robotics import DriveBase
from pybricks.tools import wait
from sounds import playTune


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
lastRgb = None

# Color RGB Reference Values...INITIAL SETUP REQUIRED 
colorReferences = {
    "RED": (71, 10, 9),
    "GREEN": (5, 28, 15),
    "BLUE": (6, 10, 14),
    "YELLOW": (76, 40, 10),
    "FLOOR": (63, 73, 99)
}

# Stop Colors: Pick which colors to stop on based on which ones end up being the pickup and dropoff locations...DISABLED UNTIL TESTING IS DONE
stopColors = [
    # "RED",
    # "GREEN",
    "BLUE",
    # "YELLOW"
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
# right sensor reading above this means there is an opening
openDistance = 500
# distance the ultrasnoic sensor should read to keep the robot hugging the right wall
rightWallDistance = 250
# when the robot sees an openDistance it then drives this distance before making the right turn so that it doesnt turn and then clip a wall
clearCornerDistance = 300
# after turning from finding an openDistance, there will be an openDistance so this stops it from turning again until it has driven this distance
newPathDistance = 350
# wheel distance where the current right-side opening was first seen
openingStart = None
# ignores right right side openings until this distance is traveled
ignoreRightUntil = 0


# Server configuration
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 12345))
server_socket.listen(1)
print("Waiting for connection...")
client_socket, address = server_socket.accept()
print("Connected to {}".format(address))

#  added setBlocking so that the Color Sensor and UltraSonic Searches all the time.
client_socket.setblocking(False)


try:
    
    while True:

        # Ultrasonic Sensor Enabled
        currentDistance = ultrasonicSensor.distance()
        # if currentDistance != lastDistance:
        #     ev3.screen.clear()
        #     ev3.screen.print(currentDistance)
        #     lastDistance = currentDistance
        
        currentAngle = gyroSensor.angle()
        # if currentAngle != lastAngle:
        #     ev3.screen.clear()
        #     ev3.screen.print(currentAngle)
        #     lastAngle = currentAngle

        # Touch Sensor Enabled
        # if touchSensor.pressed():
        #     robot.stop()
        #     ev3.speaker.beep(frequency=440, duration=100)
        #     robot.drive(-200, 0)
        #     wait(1000)
        #     robot.stop()
        #     targetAngle = currentAngle - 90
        #     while (abs(targetAngle - gyroSensor.angle()) > 3):
        #         robot.drive(0, 90)
        #     robot.stop()

        #     try: 
        #         while client_socket.recv(1024):
        #             pass
        #     except OSError:
        #         pass
        
        # Color Sensor Enabled...MORE TESTING REQUIRED

        r, g, b = colorSensor.rgb()
        if (r, g, b) != lastRgb:
            ev3.screen.clear()
            ev3.screen.print(r, g, b)
            lastRgb = (r, g, b)
 
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
                autoMode = False
                robot.stop()
                ev3.screen.clear()              
                ev3.screen.print(currentColor)  
                ev3.speaker.beep(frequency=440, duration=100)
                try:
                    while client_socket.recv(2):
                        pass
                except OSError:
                    pass
        else:
            onTape = False

        # Gyro Sensor Enabled
        

        if autoMode:
            if touchSensor.pressed():
                robot.stop()
                ev3.speaker.beep(frequency=440, duration=100)
                # may need to adjust the back up to make sure its in the center of the block...but should get corrected with the steering correction below.
                robot.drive(-200, 0)
                wait(1000)
                robot.stop()
                targetAngle = currentAngle + 90
                while (abs(targetAngle - gyroSensor.angle()) > 3):
                    robot.drive(0, -90)
                robot.stop()
                robot.reset()
                openingStart = None
                ignoreRightUntil = 0

                try: 
                    while client_socket.recv(1024):
                        pass
                except OSError:
                    pass

            elif currentDistance > openDistance:
                if robot.distance() < ignoreRightUntil:
                    robot.drive(200, 0)
                else:
                    if openingStart is None:
                        openingStart = robot.distance()
                    if robot.distance() - openingStart >= clearCornerDistance:
                        robot.stop()
                        targetAngle = gyroSensor.angle() - 90
                        while (abs(targetAngle - gyroSensor.angle()) > 3):
                            robot.drive(0, 90)
                        robot.stop()
                        robot.reset()
                        openingStart = None
                        ignoreRightUntil = newPathDistance
                    else:
                        robot.drive(200, 0)

            else:
                openingStart = None
                # if it moves away from the wall instead of hugging the 0.5 needs to change to -0.5
                steeringCorrection = (currentDistance - rightWallDistance) * 0.5
                steeringCorrection = max(-40, min(40, steeringCorrection))
                robot.drive(200, steeringCorrection)

        try:
            command = client_socket.recv(2).decode()
        except OSError:
            wait(10)
            continue
        if not command:
            break   
        
        # Keyboard Commands for Movement
        key, action = command[0], command[1]

        
        # AutoMode Stops WASD and Weapon Input
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