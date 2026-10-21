from pybricks.tools import StopWatch

# miliseconds...I set it to 1000 seconds so that it would beep every 1 second can be adjusted based on the variables below.
beepInterval = 1000
beepFrequency = 500  
beepDuration = 30    
 
beepTimer = StopWatch()
 
def beepIfDue(ev3):
    if beepTimer.time() >= beepInterval:
        ev3.speaker.beep(frequency=beepFrequency, duration=beepDuration)
        beepTimer.reset()