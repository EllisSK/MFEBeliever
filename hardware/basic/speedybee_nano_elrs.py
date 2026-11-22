import machine as m
import math
import struct as s
import utime as t


CRSF_SYNC_BYTE = 0xC8
CRSF_BROADCAST_ADDRESS = 0x00
_FRAME_START_BYTES = (CRSF_SYNC_BYTE, CRSF_BROADCAST_ADDRESS)
CRSF_MAX_PACKET_LEN = 64
CRSF_CHANNEL_VALUE_MIN = 172
CRSF_CHANNEL_VALUE_MID = 992
CRSF_CHANNEL_VALUE_MAX = 1811

FRAME_TYPE_GPS = 0x02
FRAME_TYPE_BATTERY_SENSOR = 0x08
FRAME_TYPE_BAROMETRIC_ALTITUDE = 0x09
FRAME_TYPE_LINK_STATISTICS = 0x14
FRAME_TYPE_RC_CHANNELS_PACKED = 0x16
FRAME_TYPE_ATTITUDE = 0x1E
FRAME_TYPE_FLIGHT_MODE = 0x21
FRAME_TYPE_ARDUPILOT_TELEMETRY = 0x80
STATUS_TEXT_SUBTYPE = 0xF1
STATUS_WARNING = 4
STATUS_INFO = 6


def _crc8_table():
    table = bytearray(256)
    for i in range(256):
        crc = i
        for _ in range(8):
            crc = ((crc << 1) ^ (0xD5 if crc & 0x80 else 0)) & 0xFF
        table[i] = crc
    return table


_CRC8_TABLE = _crc8_table()


class SpeedyBeeNanoELRS(m.UART):
    def __init__(self, uart_id, tx_pin, rx_pin, baudrate=420000):
        super().__init__(
            uart_id, baudrate=baudrate, tx=m.Pin(tx_pin), rx=m.Pin(rx_pin),
            bits=8, parity=None, stop=1, rxbuf=CRSF_MAX_PACKET_LEN * 4
        )
        self.channels = [CRSF_CHANNEL_VALUE_MID] * 16
        self.link_quality = 0
        self.rssi_dbm = 0
        self.last_packet_time = None
        self._last_rc_time = None
        self._buffer = b""
        self._recovering = False

    def _calculate_crc8(self, data):
        crc = 0
        for byte in data:
            crc = _CRC8_TABLE[crc ^ byte]
        return crc

    def update(self):
        waiting = self.any()
        if not waiting:
            return False
        chunk = self.read(min(waiting, CRSF_MAX_PACKET_LEN * 4))
        if not chunk:
            return False

        data = self._buffer + chunk
        offset = 0
        pending = None
        received = False
        while offset + 2 <= len(data):
            if data[offset] not in _FRAME_START_BYTES:
                offset += 1
                continue

            length = data[offset + 1]
            if not 2 <= length <= CRSF_MAX_PACKET_LEN - 2:
                offset += 1
                continue

            end = offset + 2 + length
            if end > len(data):
                if not self._recovering:
                    break
                if pending is None:
                    pending = offset
                offset += 1
                continue

            body = data[offset + 2:end - 1]
            if self._calculate_crc8(body) != data[end - 1]:
                self._recovering = True
                offset += 1
                continue

            self._recovering = False
            pending = None
            if self._handle_frame(body[0], body[1:]):
                self.last_packet_time = t.ticks_ms()
                received = True
            offset = end
            if data[end - 1] in _FRAME_START_BYTES:
                # A dropped byte can make the next frame's sync byte look like a CRC.
                offset -= 1
                self._recovering = True

        self._buffer = data[pending if pending is not None else offset:]
        return received

    def _handle_frame(self, frame_type, payload):
        if frame_type == FRAME_TYPE_RC_CHANNELS_PACKED:
            if len(payload) != 22:
                return False
            self._parse_rc_channels(payload)
            self._last_rc_time = t.ticks_ms()
        elif frame_type == FRAME_TYPE_LINK_STATISTICS:
            if len(payload) < 10:
                return False
            self._parse_link_statistics(payload)
        return True

    def _parse_rc_channels(self, payload):
        value = 0
        bits = 0
        channel = 0
        for byte in payload:
            value |= byte << bits
            bits += 8
            if bits >= 11:
                self.channels[channel] = value & 0x7FF
                value >>= 11
                bits -= 11
                channel += 1

    def _parse_link_statistics(self, payload):
        antenna = 1 if payload[4] == 1 else 0
        self.rssi_dbm = -payload[antenna]
        self.link_quality = payload[2]

    def is_connected(self, timeout_ms=1000):
        if self._last_rc_time is None:
            return False
        return 0 <= t.ticks_diff(t.ticks_ms(), self._last_rc_time) < timeout_ms

    def get_channel_percent(self, channel_index):
        if not 0 <= channel_index < len(self.channels):
            return 0.0
        raw = self.channels[channel_index]
        raw = max(CRSF_CHANNEL_VALUE_MIN, min(raw, CRSF_CHANNEL_VALUE_MAX))
        if raw < CRSF_CHANNEL_VALUE_MID:
            span = CRSF_CHANNEL_VALUE_MID - CRSF_CHANNEL_VALUE_MIN
        else:
            span = CRSF_CHANNEL_VALUE_MAX - CRSF_CHANNEL_VALUE_MID
        return (raw - CRSF_CHANNEL_VALUE_MID) * 100.0 / span

    def _send_packet(self, frame_type, payload):
        length = len(payload) + 2
        if length > CRSF_MAX_PACKET_LEN - 2:
            raise ValueError("CRSF payload is too long")
        frame = bytes((frame_type,)) + payload
        crc = self._calculate_crc8(frame)
        packet = bytes((CRSF_SYNC_BYTE, length)) + frame + bytes((crc,))
        return self.write(packet) == len(packet)

    def send_status_text(self, message, severity=STATUS_INFO):
        if not 0 <= severity <= 7:
            raise ValueError("Status severity must be between 0 and 7")
        text = message.split("\x00", 1)[0].encode("utf-8")
        limit = 49
        while limit < len(text) and text[limit] & 0xC0 == 0x80:
            limit -= 1
        payload = bytes((STATUS_TEXT_SUBTYPE, severity)) + text[:limit] + b"\x00"
        return self._send_packet(FRAME_TYPE_ARDUPILOT_TELEMETRY, payload)

    def send_battery_sensor(self, voltage, current, capacity_mah, remaining_percent=0):
        voltage = max(0, min(int(round(voltage * 10)), 0x7FFF))
        current = max(-0x8000, min(int(round(current * 10)), 0x7FFF))
        capacity = max(0, min(int(capacity_mah), 0xFFFFFF))
        remaining = max(0, min(int(remaining_percent), 100))
        payload = s.pack(">hh", voltage, current)
        payload += bytes((capacity >> 16, (capacity >> 8) & 0xFF, capacity & 0xFF, remaining))
        return self._send_packet(FRAME_TYPE_BATTERY_SENSOR, payload)

    def send_barometric_altitude(self, altitude_m):
        decimetres = int(round(altitude_m * 10))
        if decimetres < 0x8000 - 10_000:
            altitude = max(0, decimetres + 10_000)
        else:
            altitude = 0x8000 | min(0x7FFE, (decimetres + 5) // 10)
        return self._send_packet(FRAME_TYPE_BAROMETRIC_ALTITUDE, s.pack(">H", altitude))

    def send_gps(self, latitude, longitude, altitude_m, satellites):
        lat = int(latitude * 1e7)
        lon = int(longitude * 1e7)
        alt = max(0, min(int(altitude_m) + 1000, 0xFFFF))
        satellites = max(0, min(int(satellites), 0xFF))
        payload = s.pack(">iiHHHB", lat, lon, 0, 0, alt, satellites)
        return self._send_packet(FRAME_TYPE_GPS, payload)

    def send_attitude(self, pitch_deg, roll_deg, yaw_deg):
        scale = math.pi / 180 * 10_000
        angles = tuple(
            int(((angle + 180) % 360 - 180) * scale)
            for angle in (pitch_deg, roll_deg, yaw_deg)
        )
        return self._send_packet(FRAME_TYPE_ATTITUDE, s.pack(">hhh", *angles))

    def send_flight_mode(self, mode_string):
        return self._send_packet(FRAME_TYPE_FLIGHT_MODE, mode_string.encode("ascii") + b"\x00")
