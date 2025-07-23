import machine as m
import utime as t
from emax_generic_servo import EmaxGenericServo

class EmaxES08MDII(EmaxGenericServo):
    def __init__(self, pwm_pin: int):
        super().__init__(
            pwm_pin=pwm_pin
        )