from pybricks.tools import wait
 
 
def playTune(ev3, num):
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