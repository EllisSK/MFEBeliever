import machine as m
import utime as t

class GenericBuzzer(m.Pin):
    def __init__(self, pin, active_high=True):
        self._active = int(bool(active_high))
        super().__init__(pin, m.Pin.OUT, value=1 - self._active)

    def on(self):
        self.value(self._active)

    def off(self):
        self.value(1 - self._active)

    def beep(self, duration_ms=100):
        if duration_ms < 0:
            raise ValueError("Buzzer duration must be nonnegative")
        self.on()
        try:
            t.sleep_ms(duration_ms)
        finally:
            self.off()
