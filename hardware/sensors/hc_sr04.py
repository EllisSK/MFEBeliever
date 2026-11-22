import machine as m
import utime as t

class HCSR04:
    def __init__(self, trigger_pin, echo_pin, timeout_us=30_000):
        if timeout_us <= 0:
            raise ValueError("Echo timeout must be positive")
        self._trigger = m.Pin(trigger_pin, m.Pin.OUT, value=0)
        self._echo = m.Pin(echo_pin, m.Pin.IN)
        self._timeout_us = timeout_us
        self._last_trigger = None

    def read_distance_cm(self):
        if self._last_trigger is not None:
            elapsed = t.ticks_diff(t.ticks_ms(), self._last_trigger)
            if 0 <= elapsed < 60:
                t.sleep_ms(60 - elapsed)

        self._last_trigger = t.ticks_ms()
        self._trigger.on()
        try:
            t.sleep_us(10)
        finally:
            self._trigger.off()
        pulse = m.time_pulse_us(self._echo, 1, self._timeout_us)
        distance = pulse / 58
        if 2 <= distance <= 400:
            return distance
        return None
