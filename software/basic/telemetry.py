import utime as t

from hardware.basic.speedybee_nano_elrs import STATUS_INFO, STATUS_WARNING


class Telemetry:
    STATUS_INTERVAL_MS = 1000
    MAX_PENDING_MESSAGES = 12

    def __init__(self, radio, battery_warning_v=None, battery_capacity_mah=None):
        if battery_warning_v is not None and battery_warning_v <= 0:
            raise ValueError("Battery warning voltage must be positive")
        if battery_capacity_mah is not None and battery_capacity_mah <= 0:
            raise ValueError("Battery capacity must be positive")

        self.radio = radio
        self.connected = False
        self._had_link = False
        self._messages = []
        self._last_status_attempt = None
        self._write_failed = False
        self._failed_devices = set()
        self._has_fix = False
        self._battery_warning_v = battery_warning_v
        self._battery_capacity_mah = battery_capacity_mah
        self._battery_low = False
        self._last_current = None
        self._consumed_mah = 0.0
        self._ground_pressure = None

    def notify(self, message, severity=STATUS_INFO):
        print(message)
        if self.radio is not None:
            if len(self._messages) == self.MAX_PENDING_MESSAGES:
                self._messages.pop(0)
            self._messages.append((message, severity))

    def guide(self, message, severity=STATUS_INFO):
        print(message)
        if self.radio is not None:
            self.send(self.radio.send_status_text, message, severity)

    def send(self, operation, *args):
        try:
            written = operation(*args)
        except OSError:
            written = False
        if not written and not self._write_failed:
            print("Radio telemetry write failed")
        self._write_failed = not written
        return written

    def read(self, name, operation, *args, **kwargs):
        try:
            value = operation(*args, **kwargs)
        except OSError as error:
            if name not in self._failed_devices:
                self._failed_devices.add(name)
                self.notify(name + " unavailable", STATUS_WARNING)
                print(error)
            return None

        if name in self._failed_devices:
            self._failed_devices.remove(name)
            self.notify(name + " responding")
        return value

    def update(self):
        if self.radio is None:
            return

        self.read("Radio UART", self.radio.update)
        connected = self.radio.is_connected()
        if connected != self.connected:
            self.connected = connected
            if connected:
                self.notify("RC link restored" if self._had_link else "RC link connected")
                self._had_link = True
                self._last_status_attempt = None
            else:
                self.notify("RC link lost", STATUS_WARNING)

        if self.connected and self._messages:
            now = t.ticks_ms()
            if (self._last_status_attempt is None
                    or t.ticks_diff(now, self._last_status_attempt) >= self.STATUS_INTERVAL_MS):
                self._last_status_attempt = now
                if self.send(self.radio.send_status_text, *self._messages[0]):
                    self._messages.pop(0)

    def publish(self, now, fix, battery, barometer):
        self._publish_gps(fix)
        self._publish_battery(now, battery)
        self._publish_barometer(barometer)
        if self.connected:
            self.send(self.radio.send_flight_mode, "GROUND")

    def _publish_gps(self, fix):
        has_fix = fix is not None
        if has_fix != self._has_fix:
            self._has_fix = has_fix
            if has_fix:
                self.notify("GPS fix acquired")
            else:
                self.notify("GPS fix lost", STATUS_WARNING)

        if has_fix and self.connected:
            self.send(self.radio.send_gps, *fix)

    def _publish_battery(self, now, battery):
        if battery is None:
            self._last_current = None
            return

        voltage, current = battery
        if self._last_current is not None:
            last_time, last_current = self._last_current
            elapsed = t.ticks_diff(now, last_time)
            if elapsed > 0:
                self._consumed_mah += (current + last_current) * elapsed / 7200
        self._last_current = (now, current)

        if self._battery_warning_v is not None:
            if not self._battery_low and voltage < self._battery_warning_v:
                self._battery_low = True
                self.notify(f"Battery voltage low ({voltage:.1f} V)", STATUS_WARNING)
            elif self._battery_low and voltage >= self._battery_warning_v + 0.3:
                self._battery_low = False
                self.notify(f"Battery voltage recovered ({voltage:.1f} V)")

        if self.connected:
            remaining = 0
            if self._battery_capacity_mah is not None:
                remaining = round(100 * (1 - self._consumed_mah / self._battery_capacity_mah))
            self.send(self.radio.send_battery_sensor, voltage, current, self._consumed_mah, remaining)

    def _publish_barometer(self, barometer):
        if barometer is None or barometer[0] <= 0:
            return

        pressure, _ = barometer
        if self._ground_pressure is None:
            self._ground_pressure = pressure
        if self.connected:
            altitude_m = 44_330 * (1 - (pressure / self._ground_pressure) ** 0.190263)
            self.send(self.radio.send_barometric_altitude, altitude_m)
