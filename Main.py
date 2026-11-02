#!/usr/bin/env pybricks-micropython
# main.py
import socket

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor, ColorSensor, UltrasonicSensor, GyroSensor
from pybricks.parameters import Port, Color 
from pybricks.robotics import DriveBase
from pybricks.tools import wait
from sounds import playTune
from mazeFunctions import nextToBlockIAmOn, backToAPreviousBlock, mazeMapFill, getBlockSides, howManyDegreesToTurn, makingTheTurn


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
stopColors = [Color.RED, Color.GREEN, Color.BLUE, Color.YELLOW, Color.WHITE]
onTape = False


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

# Maze Mapping Initialization...TESTING REQUIRED
blockLength = 680 #approximate based on what we measured during Ultrasonic Sensor Testing...can be changed if needed
openDistance = 500 #we can change this if needed to find all open areas
mazeMapStorage = [] #ArrayList ... same as using ArrayList<class> mazeMapStorage = new ArrayList<class>(); ... this Array builds a map of the maze
visitedBlocks = [] # this ArrayList stores which blocks our robot has been to. (does not store sides of the blocks)
pathTakenBeforeDeadEnd = [] #stores path taken until the robot hits a dead end so that it knows where to go back to.
robotLocation = (0, 0) # x and y
robotFacingWhichWay = 0 # numbered like north = 0, east = 1, south = 2, west = 3
robotNeedsToFaceAngle = 0
autoStep = "startFreshRun" #resets Map, robot location, gyro to 0, and pathTakenBeforeDeadEnd
sidesThatNeedToBeChecked = [] # stores sides that havnt been determined as a wall or openning

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
            autoMode = False
            robot.stop()
            ev3.speaker.beep(frequency=440, duration=100)
        
        # Color Sensor Enabled...Blue Seeing Green
        if colorSensor.color() in stopColors:
            if not onTape:
                onTape = True
                robot.stop()
                ev3.speaker.play_file(playTune.STOP)
                wait(5000)
                try:
                    while client_socket.recv(2):
                        pass
                except OSError:
                    pass
                # ev3.speaker.play_file(SoundFile.GO)
        else:
            onTape = False

        # Gyro Sensor Enabled
        currentAngle = gyroSensor.angle()
        # if currentAngle != lastAngle: #We only need to enable this if we need to test why its not working.
        #     ev3.screen.clear()
        #     ev3.screen.print(currentAngle)
        #     lastAngle = currentAngle

        # Ultrasonic Sensor Enabled
        currentDistance = ultrasonicSensor.distance()
        # if currentDistance != lastDistance: #We only need to enable this if we need to test why its not working
        #     ev3.screen.clear()
        #     ev3.screen.print(currentDistance)
        #     lastDistance = currentDistance

        if autoMode:

            if autoStep == "startFreshRun":
                mazeMapStorage = []
                visitedBlocks = []
                robotLocation = (0, 0)
                robotFacingWhichWay = 0
                robotNeedsToFaceAngle = gyroSensor.angle()
                visitedBlocks.append(robotLocation)
                pathTakenBeforeDeadEnd = [robotLocation]
                autoStep = "blockArrival"

            elif autoStep == "blockArrival":
                #runs every time the robot stops...including the start of autoMode
                sidesOfThisBlock = getBlockSides(mazeMapStorage, robotLocation)
                if sidesOfThisBlock[robotFacingWhichWay] is None:
                    if currentDistance > openDistance:
                        mazeMapFill(mazeMapStorage, robotLocation, robotFacingWhichWay, "open")
                    else:
                        mazeMapFill(mazeMapStorage, robotLocation, robotFacingWhichWay, "wall")
                sidesThatNeedToBeChecked = []
                #check each side...if No data, append
                # same as enhanced for loop in Java: 
                # for (int sideToCheck : new int[] {(robotFacingWhichWay + 3) % 4, (robotFacingWhichWay + 1) % 4, (robotFacingWhichWay + 2) % 4})
                for sideToCheck in [(robotFacingWhichWay + 3) % 4, (robotFacingWhichWay + 1) % 4, (robotFacingWhichWay + 2) % 4]:
                    if sidesOfThisBlock[sideToCheck] is None:
                        sidesThatNeedToBeChecked.append(sideToCheck)
                autoStep = "pickUnscannedSide"

            
            elif autoStep == "pickUnscannedSide":
                # len() is the same as using .size() in java
                # if all sides are known in mazeMapStorage it moves to chooseWhereToGo
                if len(sidesThatNeedToBeChecked) == 0:
                    autoStep = "chooseWhereToGo"
                else:
                    # pop() is the same a remove() for an ArrayList in Java
                    # takes the next unchecked side off the front of the list
                    sideToCheck = sidesThatNeedToBeChecked.pop(0)
                    # sets gyro to the angle we want the robot to face
                    robotNeedsToFaceAngle += howManyDegreesToTurn(robotFacingWhichWay, sideToCheck)
                    # updates which direction the robot will be facing after the turn
                    robotFacingWhichWay = sideToCheck
                    autoStep = "turnToUnscanned"

            elif autoStep == "turnToUnscanned":
                # turns to unscanned side chosen in pickUnscannedSide
                if makingTheTurn(robot, gyroSensor, robotNeedsToFaceAngle):
                    wait(100) # settles the gyroSensor ... we can change this if we thnig the gyroSensor is still shaking
                    if ultrasonicSensor.distance() > openDistance:
                        mazeMapFill(mazeMapStorage, robotLocation, robotFacingWhichWay, "open")
                    else:
                        mazeMapFill(mazeMapStorage, robotLocation, robotFacingWhichWay, "wall")
                    autoStep = "pickUnscannedSide"

            # this will change once we figure out the color setup
            elif autoStep == "chooseWhereToGo":
                chosenDirection = None
                sidesOfThisBlock = getBlockSides(mazeMapStorage, robotLocation)
                for directionToTry in [(robotFacingWhichWay + 3) % 4, (robotFacingWhichWay + 1) % 4, robotFacingWhichWay, (robotFacingWhichWay + 2) % 4]:
                    if sidesOfThisBlock[directionToTry] == "open":
                        if nextToBlockIAmOn(robotLocation, directionToTry) not in visitedBlocks:
                            chosenDirection = directionToTry
                            break
                if chosenDirection is not None:
                    robotNeedsToFaceAngle += howManyDegreesToTurn(robotFacingWhichWay, chosenDirection)
                    robotFacingWhichWay = chosenDirection
                    autoStep = "turnToChosen"
                # elif len(pathTakenBeforeDeadEnd) ... will work differently when we have the colors setup
                elif len(pathTakenBeforeDeadEnd) <= 1:
                    robot.stop()
                    autoMode = False
                    playTune(ev3, 0)
                else:
                    # if no new places to go then it sets up the info it needs to turnBack
                    pathTakenBeforeDeadEnd.pop()
                    directionToPreviousBlock = backToAPreviousBlock(robotLocation, pathTakenBeforeDeadEnd[-1])
                    robotNeedsToFaceAngle += howManyDegreesToTurn(robotFacingWhichWay, directionToPreviousBlock)
                    robotFacingWhichWay = directionToPreviousBlock
                    autoStep = "turnBack"

            elif autoStep == "turnToChosen":
                if makingTheTurn(robot, gyroSensor, robotNeedsToFaceAngle):
                    robot.reset()
                    autoStep = "driveUntilWallOrColor"

            elif autoStep == "driveUntilWallOrColor":
                distanceToGo = currentDistance - targetDistance
                # robot may not stop fast enough to stop directly on 340 so the <=10 helps with that...it may not be necessary.
                if distanceToGo <= 10:
                    robot.stop()
                    blocksDriven = round(robot.distance() / blockLength)
                    if blocksDriven < 1:
                        blocksDriven = 1
                    for blockNumber in range(blocksDriven):
                        mazeMapFill(mazeMapStorage, robotLocation, robotFacingWhichWay, "open")
                        robotLocation = nextToBlockIAmOn(robotLocation, robotFacingWhichWay)
                        if robotLocation not in visitedBlocks:
                            visitedBlocks.append(robotLocation)
                        pathTakenBeforeDeadEnd.append(robotLocation)
                    autoStep = "blockArrival"
                else:
                    driveSpeed = distanceToGo * 2
                    driveSpeed = max(-300, min(300, driveSpeed))
                    # keeps driving straight...may need to change if it doesnt.
                    steeringCorrection = (gyroSensor.angle() - robotNeedsToFaceAngle) * 2   
                    robot.drive(driveSpeed, steeringCorrection)

            elif autoStep == "turnBack":
                if makingTheTurn(robot, gyroSensor, robotNeedsToFaceAngle):
                    robot.reset()
                    autoStep = "driveOneBlockBack"

            elif autoStep == "driveOneBlockBack":
                distanceLeftInBlock = blockLength - robot.distance()
                if distanceLeftInBlock <= 10:
                    robot.stop()
                    robotLocation = pathTakenBeforeDeadEnd[-1]
                    autoStep = "blockArrival"
                else:
                    driveSpeed = distanceLeftInBlock * 2
                    driveSpeed = max(-300, min(300, driveSpeed))
                    steeringCorrection = (gyroSensor.angle() - robotNeedsToFaceAngle) * 2   # keeps it driving straight
                    robot.drive(driveSpeed, steeringCorrection)

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

        
        # AutoMode Stops WASD and Weapon Input
        if key == " ":
            if action == "d":
                autoMode = not autoMode
                autoStep = "startFreshRun"
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
