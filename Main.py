#!/usr/bin/env pybricks-micropython
# main.py
import socket
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase


# Initialize EV3 components
ev3 = EV3Brick()
left_motor = Motor(Port.C)
right_motor = Motor(Port.D)
# weapon = Motor(Port.A)
robot = DriveBase(left_motor, right_motor, wheel_diameter=55.5, axle_track=104)


# Server configuration
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 12345))
server_socket.listen(1)
print("Waiting for connection...")
client_socket, address = server_socket.accept()
print("Connected to {}".format(address))


try:
    while True:
       
        command = client_socket.recv(2).decode()
        if not command:
            break


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
