import machine as m
import utime as t

class EmaxGenericServo(m.I2C):
    def __init__(self, pwm_pin: int):
        pass