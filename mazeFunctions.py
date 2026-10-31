
def nextToBlockIAmOn(givenBlock, givenDirection):
    # function that shows which block is next to the given block, in the given direction
    # used by chooseWhereToGo, backToAPreviousBlock, driveUntilWallOrColor, and mazeMapFill
    x, y = givenBlock
    # set up like a graph x and y axis ... each x, y is a block in the maze
    # it adds or subtracts to get the location of the block next to it
    if givenDirection == 0:
        return (x, y + 1)
    if givenDirection == 1:
        return (x + 1, y)
    if givenDirection == 2:
        return (x, y - 1)
    return (x - 1, y)
 
 
def backToAPreviousBlock(blockRobotIsIn, previousBlock):
    # function that shows which direction the robot needs to face to get to the previous block
    # used by chooseWhereToGo when no open side leads to a block it hasn't visited yet
    for directionToTry in range(4): # 4 is just using directionToTry < 4; in a for loop in java
        # tries all 4 directions until one of them leads to the previous block
        if nextToBlockIAmOn(blockRobotIsIn, directionToTry) == previousBlock:
            return directionToTry
    return None
 
 
def getBlockSides(mazeMapStorage, blockToFind):
    # function that searches the map for a block and gives back its list of 4 sides
    # used by blockArrival, chooseWhereToGo, and mazeMapFill
    # example of what it is grabbing from mazeMapStorage  ["open", "wall", None, None] from a block (x, y) 
    for blockAndSides in mazeMapStorage:
        if blockAndSides[0] == blockToFind: # 0 is blocks location
            return blockAndSides[1] # 1 is blocks sides
 
    # if the block doesnt exist is creates it
    sidesOfNewBlock = [None, None, None, None] # None is pythons Null
    mazeMapStorage.append([blockToFind, sidesOfNewBlock]) # .append adds to end like .add() in Java
    return sidesOfNewBlock
 
 
def mazeMapFill(mazeMapStorage, blockBeingChecked, sideBeingChecked, wallOrOpen):
    # function that writes "wall" or "open" into the map for one side of a block
    # used by blockArrival, turnToUnscanned, and driveUntilWallOrColor
    blockSides = getBlockSides(mazeMapStorage, blockBeingChecked)
    blockSides[sideBeingChecked] = wallOrOpen
 
    # if the block on the other side shares the same wall (or opening), so it gets recorded too
    # sideBeingChecked + 2 % 4 is the opposite side, like east (1) becomes west (3)
    blockOnOtherSide = nextToBlockIAmOn(blockBeingChecked, sideBeingChecked)
    otherBlockSides = getBlockSides(mazeMapStorage, blockOnOtherSide)
    otherBlockSides[(sideBeingChecked + 2) % 4] = wallOrOpen
 
 
def howManyDegreesToTurn(robotFacingWhichWay, directionToTurnTo):
    # function that shows how many degrees the robot needs to turn to face a new direction
    # used by pickUnscannedSide and chooseWhereToGo
    rightTurnsNeeded = (directionToTurnTo - robotFacingWhichWay) % 4
    if rightTurnsNeeded == 1:
        return -90    # right
    if rightTurnsNeeded == 2:
        return 180    
    if rightTurnsNeeded == 3:
        return 90     
    return 0          #already facing correct way
 
 
def makingTheTurn(robot, gyroSensor, robotNeedsToFaceAngle):
    # function that turns the robot a little bit each loop until it faces robotNeedsToFaceAngle
    # used by turnToUnscanned, turnToChosen, and turnBack
    degreesLeftToTurn = gyroSensor.angle() - robotNeedsToFaceAngle
    if abs(degreesLeftToTurn) <= 2:
        robot.stop()
        return True # Now facing the correct way
 
    turnSpeed = degreesLeftToTurn * 3                  # slows down so it doesnt pass the the stopping point
    if turnSpeed > 0:
        turnSpeed = max(40, min(150, turnSpeed))       # can change these speeds if its moving too slow or too fast.
    else:
        turnSpeed = min(-40, max(-150, turnSpeed))
    robot.drive(0, turnSpeed)
    return False

