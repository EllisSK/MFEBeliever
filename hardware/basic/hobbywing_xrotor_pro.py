import machine as m
import utime as t


class HobbywingXRotorPro(m.PWM):
    MIN_PULSE_WIDTH_US = 1000
    MAX_PULSE_WIDTH_US = 2000

    def __init__(self, pwm_pin: int, freq: int = 50):
        if not 0 < freq <= 1_000_000 // self.MAX_PULSE_WIDTH_US:
            raise ValueError("PWM frequency is outside the ESC pulse range")

        super().__init__(
            m.Pin(pwm_pin),
            freq=freq,
            duty_ns=self.MIN_PULSE_WIDTH_US * 1000
        )

    def set_speed(self, speed: float):
        if not speed > 0:
            self.stop()
            return

        pulse_range = self.MAX_PULSE_WIDTH_US - self.MIN_PULSE_WIDTH_US
        pulse_us = self.MIN_PULSE_WIDTH_US + min(speed, 1.0) * pulse_range
        self.duty_ns(int(pulse_us * 1000))

    def stop(self):
        self.duty_ns(self.MIN_PULSE_WIDTH_US * 1000)

    def arm(self):
        self.stop()
        t.sleep_ms(2500)

    def calibrate(self):
        input("Remove the propeller and disconnect ESC power, then press Enter. ")
        try:
            self.set_speed(1.0)
            input("Connect ESC power and press Enter after the calibration beeps. ")
        finally:
            self.stop()
        t.sleep_ms(3000)
