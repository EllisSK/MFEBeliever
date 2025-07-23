import machine as m
import utime as t

class EmaxGenericServo(m.PWM):
    def __init__(self, pwm_pin: int):
        super().__init__(
            dest=m.Pin(pwm_pin),
            freq=50
        )