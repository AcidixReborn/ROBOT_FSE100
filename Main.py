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
left_motor = Motor(Port.C)
right_motor = Motor(Port.D)
# weapon = Motor(Port.A)
robot = DriveBase(left_motor, right_motor, wheel_diameter=55.5, axle_track=104)

# Touch Sensor Initialization
touchSensor = TouchSensor(Port.S1)

# Color Sensor Initialization...NEEDS TESTED BEFORE IMPLEMENTING
# colorSensor = ColorSensor(Port.S2)
# stopColors = [Color.RED, Color.GREEN, Color.BLUE, Color.YELLOW]
# onTape = False

# Gyro Sensor Initialization
# gyroSensor = GyroSensor(Port.S3)
# gyroSensor.reset_angle(0)
# lastAngle = None

# Ultrasonic Sensor Initialization...NEEDS TESTED BEFORE IMPLEMENTING
# ultrasonicSensor = UltrasonicSensor(Port.S4)
# lastDistance = None

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

        # Touch Sensor Enabled
        if touchSensor.pressed():
            robot.stop()
            ev3.speaker.beep(frequency=440, duration=100)
            break
        
        # Color Sensor Enabled...NEEDS TESTED BEFORE IMPLEMENTING
        # currentColor = colorSensor.color()
        # if currentColor in stopColors:
        #     if not onTape:
        #         onTape = True
        #         robot.stop()
        #         ev3.screen.clear()
        #         ev3.screen.print(currentColor)
        #         ev3.speaker.beep(frequency=440, duration=100)
        #         wait(5000)
        #         try:
        #             while client_socket.recv(2):
        #                 pass
        #         except OSError:
        #             pass
        #         # ev3.speaker.beep(frequency=440, duration=100)
        # else:
        #     onTape = False

        # Gyro Sensor Enabled...NEEDS TESTED BEFORE IMPLEMENTING
        # currentAngle = gyroSensor.angle()
        # if currentAngle != lastAngle:
        #     ev3.screen.clear()
        #     ev3.screen.print(currentAngle)
        #     lastAngle = currentAngle

        # Ultrasonic Sensor Enabled...NEEDS TESTED BEFORE IMPLEMENTING
        # currentDistance = ultrasonicSensor.distance()
        # if currentDistance != lastDistance:
        #     ev3.screen.clear()
        #     ev3.screen.print(currentDistance)
        #     lastDistance = currentDistance

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
