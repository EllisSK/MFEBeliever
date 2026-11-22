import machine as m
import utime as t


class UbloxNeoM9N:
    def __init__(self, uart_id, tx_pin, rx_pin, baudrate=38400):
        self._uart = m.UART(
            uart_id, baudrate=baudrate, tx=m.Pin(tx_pin), rx=m.Pin(rx_pin),
            bits=8, parity=None, stop=1, rxbuf=1024
        )
        self._buffer = b""
        self._fix = None
        self._last_fix_time = None

    def update(self):
        waiting = self._uart.any()
        if not waiting:
            return False

        data = self._buffer + (self._uart.read(min(waiting, 1024)) or b"")
        lines = data.split(b"\n")
        self._buffer = lines[-1] if len(lines[-1]) <= 128 else b""

        updated = False
        for line in lines[:-1]:
            start = line.rfind(b"$")
            if start >= 0 and self._parse_gga(line[start + 1:].rstrip(b"\r")):
                updated = True
        return updated

    def _parse_gga(self, line):
        end = line.find(b"*")
        if end < 0 or end != len(line) - 3 or line[2:6] != b"GGA,":
            return False

        checksum = 0
        for byte in line[:end]:
            checksum ^= byte
        try:
            if checksum != int(line[end + 1:].decode(), 16):
                return False
            fields = line[:end].decode().split(",")
            if len(fields) < 11:
                return False
            quality = int(fields[6])
            if quality <= 0:
                self._fix = None
                self._last_fix_time = None
            else:
                latitude = self._coordinate(fields[2], fields[3], "N", "S", 90)
                longitude = self._coordinate(fields[4], fields[5], "E", "W", 180)
                self._fix = (latitude, longitude, float(fields[9]), int(fields[7]))
                self._last_fix_time = t.ticks_ms()
        except (ValueError, OverflowError):
            return False
        return True

    def _coordinate(self, value, direction, positive, negative, limit):
        value = float(value)
        degrees = int(value // 100)
        minutes = value - degrees * 100
        coordinate = degrees + minutes / 60
        if not (0 <= coordinate <= limit and 0 <= minutes < 60):
            raise ValueError("Invalid NMEA coordinate")
        if direction not in (positive, negative):
            raise ValueError("Invalid NMEA hemisphere")
        return -coordinate if direction == negative else coordinate

    def get_fix(self, timeout_ms=2000):
        """Return latitude, longitude, altitude in metres, and satellite count."""
        if self._last_fix_time is None:
            return None
        if 0 <= t.ticks_diff(t.ticks_ms(), self._last_fix_time) < timeout_ms:
            return self._fix
        return None
