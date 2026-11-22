import machine as m

class EmaxGenericServo(m.PWM):
    def __init__(self, pwm_pin: int):
        super().__init__(
            m.Pin(pwm_pin),
            freq=50,
            duty_u16=0
        )

    def set_pulse_us(self, pulse_us):
        if not 0 < pulse_us < 20_000:
            raise ValueError("Servo pulse must be shorter than the PWM period")
        self.duty_ns(int(pulse_us * 1000))
