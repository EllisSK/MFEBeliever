import machine as m
import utime as t
import struct as s

# --- CRSF Protocol Constants ---
CRSF_SYNC_BYTE = 0xC8

# Frame Types
FRAME_TYPE_GPS = 0x02
FRAME_TYPE_BATTERY_SENSOR = 0x08
FRAME_TYPE_LINK_STATISTICS = 0x14
FRAME_TYPE_RC_CHANNELS_PACKED = 0x16
FRAME_TYPE_ATTITUDE = 0x1E
FRAME_TYPE_FLIGHT_MODE = 0x21

# Other constants
CRSF_MAX_PACKET_LEN = 64
CRSF_CHANNEL_VALUE_MID = 992
CRSF_CHANNEL_VALUE_MAX = 1811

class SpeedyBeeNanoELRS(m.UART):
    """
    Manages bidirectional communication with an ELRS/CRSF receiver,
    acting as a flight controller by receiving RC commands and sending telemetry.
    """
    def __init__(self, uart_id, tx_pin, rx_pin, baudrate=420000):
        """
        Initializes the SpeedyBeeNanoELRS receiver.

        Args:
            uart_id (int): The ID of the UART peripheral to use.
            tx_pin (int): The GPIO pin number for the UART TX (REQUIRED for sending).
            rx_pin (int): The GPIO pin number for the UART RX.
            baudrate (int): The baud rate for communication.
        """
        super().__init__(uart_id, baudrate=baudrate, tx=m.Pin(tx_pin), rx=m.Pin(rx_pin), bits=8, parity=None, stop=1, rxbuf=CRSF_MAX_PACKET_LEN * 2)

        # CRC8 lookup table for DVB-S2 (Polynomial 0xD5)
        self._crc_table = [
            0x00, 0xD5, 0x7F, 0xAA, 0xF4, 0x21, 0x8B, 0x5E, 0x93, 0x46, 0xEC, 0x39,
            0xCD, 0x18, 0xB2, 0x67, 0x8F, 0x5A, 0xF0, 0x25, 0xDF, 0x0A, 0xA0, 0x75,
            0xB8, 0x6D, 0xC7, 0x12, 0x4C, 0x99, 0x33, 0xE6, 0x3B, 0xEE, 0x44, 0x91,
            0x6B, 0xBE, 0x14, 0xC1, 0x0C, 0xD9, 0x73, 0xA6, 0x58, 0x8D, 0x27, 0xF2,
            0xD2, 0x07, 0xAD, 0x78, 0x86, 0x53, 0xF9, 0x2C, 0xEB, 0x3E, 0x94, 0x41,
            0xBD, 0x68, 0xC2, 0x17, 0x71, 0xA4, 0x0E, 0xDB, 0x25, 0xF0, 0x5A, 0x8F,
            0x42, 0x97, 0x3D, 0xE8, 0x16, 0xC3, 0x69, 0xBC, 0x54, 0x81, 0x2B, 0xFE,
            0x00, 0xD5, 0x7F, 0xAA, 0x67, 0xB2, 0x18, 0xCD, 0x33, 0xE6, 0x4C, 0x99,
            0xA4, 0x71, 0xDB, 0x0E, 0xF0, 0x25, 0x8F, 0x5A, 0x97, 0x42, 0xE8, 0x3D,
            0xC3, 0x16, 0xBC, 0x69, 0x81, 0x54, 0xFE, 0x2B, 0xDA, 0x0F, 0xA5, 0x70,
            0xB9, 0x6C, 0xC6, 0x13, 0x4D, 0x98, 0x32, 0xE7, 0xE9, 0x3C, 0x96, 0x43,
            0xB9, 0x6C, 0xC6, 0x13, 0xDF, 0x0A, 0xA0, 0x75, 0x8B, 0x5E, 0xF4, 0x21,
            0x49, 0x9C, 0x36, 0xE3, 0x19, 0xCC, 0x66, 0xB3, 0x7E, 0xAB, 0x01, 0xD4,
            0x2A, 0xFF, 0x55, 0x80, 0xF7, 0x22, 0x88, 0x5D, 0xA3, 0x76, 0xDC, 0x09,
            0xC4, 0x11, 0xBB, 0x6E, 0x90, 0x45, 0xEF, 0x3A, 0x10, 0xC5, 0x6F, 0xBA,
            0x44, 0x91, 0x3B, 0xEE, 0x23, 0xF6, 0x5C, 0x89, 0x77, 0xA2, 0x08, 0xDD,
            0xB5, 0x60, 0xCA, 0x1F, 0xE1, 0x34, 0x9E, 0x4B, 0x86, 0x53, 0xF9, 0x2C,
            0xD2, 0x07, 0xAD, 0x78, 0x30, 0xE5, 0x4F, 0x9A, 0x64, 0xB1, 0x1B, 0xCE,
            0x03, 0xD6, 0x7C, 0xA9, 0x57, 0x82, 0x28, 0xFD, 0x60, 0xB5, 0x1F, 0xCA,
            0x34, 0xE1, 0x4B, 0x9E, 0x53, 0x86, 0x2C, 0xF9, 0x07, 0xD2, 0x78, 0xAD,
            0x27, 0xF2, 0x58, 0x8D, 0x73, 0xA6, 0x0C, 0xD9, 0x14, 0xC1, 0x6B, 0xBE,
            0x40, 0x95, 0x3F, 0xEA
        ]
        
        # Attributes for storing latest RECEIVED data
        self.channels = [CRSF_CHANNEL_VALUE_MID] * 16
        self.link_quality = 0
        self.rssi_dbm = 0
        self.last_packet_time = 0

    def _calculate_crc8(self, data):
        crc = 0
        for byte in data:
            crc = self._crc_table[crc ^ byte]
        return crc

    # --- RECEIVING METHODS (UPLINK: Radio -> Receiver -> FC) ---

    def update(self):
        """
        Reads the UART for incoming data (RC channels, link stats) from the receiver.
        Call this frequently in the main loop.
        Returns: True if a valid packet was received and parsed, False otherwise.
        """
        if self.any() < 2:
            return False

        header = self.read(1)
        if not header or header[0] != CRSF_SYNC_BYTE:
            self.read(self.any())
            return False

        length_byte = self.read(1)
        if not length_byte: return False
        frame_length = length_byte[0]
        
        if not (2 <= frame_length <= CRSF_MAX_PACKET_LEN - 2): return False

        packet_data = self.read(frame_length)
        if not packet_data or len(packet_data) != frame_length: return False

        data_to_check = packet_data[:-1]
        received_crc = packet_data[-1]
        if received_crc != self._calculate_crc8(data_to_check): return False

        frame_type = packet_data[0]
        payload = packet_data[1:-1]

        if frame_type == FRAME_TYPE_RC_CHANNELS_PACKED:
            self._parse_rc_channels(payload)
        elif frame_type == FRAME_TYPE_LINK_STATISTICS:
            self._parse_link_statistics(payload)
        
        self.last_packet_time = t.ticks_ms()
        return True

    def _parse_rc_channels(self, payload):
        self.channels[0]  = ((payload[0] | payload[1] << 8) & 0x07FF)
        self.channels[1]  = ((payload[1] >> 3 | payload[2] << 5) & 0x07FF)
        self.channels[2]  = ((payload[2] >> 6 | payload[3] << 2 | payload[4] << 10) & 0x07FF)
        self.channels[3]  = ((payload[4] >> 1 | payload[5] << 7) & 0x07FF)
        self.channels[4]  = ((payload[5] >> 4 | payload[6] << 4) & 0x07FF)
        self.channels[5]  = ((payload[6] >> 7 | payload[7] << 1 | payload[8] << 9) & 0x07FF)
        self.channels[6]  = ((payload[8] >> 2 | payload[9] << 6) & 0x07FF)
        self.channels[7]  = ((payload[9] >> 5 | payload[10] << 3) & 0x07FF)
        self.channels[8]  = ((payload[11] | payload[12] << 8) & 0x07FF)
        self.channels[9]  = ((payload[12] >> 3 | payload[13] << 5) & 0x07FF)
        self.channels[10] = ((payload[13] >> 6 | payload[14] << 2 | payload[15] << 10) & 0x07FF)
        self.channels[11] = ((payload[15] >> 1 | payload[16] << 7) & 0x07FF)
        self.channels[12] = ((payload[16] >> 4 | payload[17] << 4) & 0x07FF)
        self.channels[13] = ((payload[17] >> 7 | payload[18] << 1 | payload[19] << 9) & 0x07FF)
        self.channels[14] = ((payload[18] >> 2 | payload[19] << 6) & 0x07FF)
        self.channels[15] = ((payload[19] >> 5 | payload[20] << 3) & 0x07FF)

    def _parse_link_statistics(self, payload):
        self.rssi_dbm = -payload[4]
        self.link_quality = payload[5]

    def is_connected(self, timeout_ms=1000):
        return (t.ticks_diff(t.ticks_ms(), self.last_packet_time) < timeout_ms)

    def get_channel_percent(self, channel_index):
        if not (0 <= channel_index < 16): return 0.0
        raw_val = self.channels[channel_index]
        return ((raw_val - CRSF_CHANNEL_VALUE_MID) / (CRSF_CHANNEL_VALUE_MAX - CRSF_CHANNEL_VALUE_MID)) * 100.0

    # --- SENDING METHODS (DOWNLINK: FC -> Receiver -> Radio) ---

    def _send_packet(self, frame_type, payload):
        """Constructs and sends a CRSF packet."""
        # Length = Type (1) + Payload + CRC (1)
        length = len(payload) + 2
        
        # Frame starts with Type and Payload
        frame = bytearray([frame_type]) + payload
        
        # Calculate CRC on the frame
        crc = self._calculate_crc8(frame)
        
        # Construct the full packet: Sync, Length, Frame, CRC
        packet = bytearray([CRSF_SYNC_BYTE, length]) + frame + bytearray([crc])
        
        self.write(packet)

    def send_battery_sensor(self, voltage, current, capacity_mah):
        """
        Sends battery telemetry (Frame 0x08).
        Args:
            voltage (float): Volts (e.g., 16.8)
            current (float): Amps (e.g., 25.5)
            capacity_mah (int): Consumed capacity in mAh (e.g., 1250)
        """
        # Pack values into the required format:
        # Voltage: uint16_t, V * 10
        # Current: uint16_t, A * 10
        # Capacity: uint24_t, mAh
        v = int(voltage * 10)
        c = int(current * 10)
        
        # Use struct to pack voltage and current (big-endian)
        payload = s.pack('>HH', v, c)
        
        # Manually pack the 24-bit capacity (big-endian)
        payload += bytearray([(capacity_mah >> 16) & 0xFF, (capacity_mah >> 8) & 0xFF, capacity_mah & 0xFF])
        
        # Add the final 'remaining %' byte (not used here, set to 0)
        payload += bytearray([0])
        
        self._send_packet(FRAME_TYPE_BATTERY_SENSOR, payload)

    def send_gps(self, latitude, longitude, altitude_m, satellites):
        """
        Sends GPS telemetry (Frame 0x02).
        Args:
            latitude (float): e.g., 37.7749
            longitude (float): e.g., -122.4194
            altitude_m (int): Altitude in meters
            satellites (int): Number of satellites
        """
        # Pack values into the required format:
        # Lat/Lon: int32_t, degrees * 1e7
        # Groundspeed: uint16_t, km/h / 10 (not used)
        # Heading: uint16_t, degrees / 100 (not used)
        # Altitude: uint16_t, meters + 1000m offset
        # Satellites: uint8_t
        lat = int(latitude * 1e7)
        lon = int(longitude * 1e7)
        alt = int(altitude_m) + 1000
        
        # Use struct to pack the main values (big-endian)
        # We send 0 for groundspeed and heading
        payload = s.pack('>iiHHHB', lat, lon, 0, 0, alt, satellites)
        
        self._send_packet(FRAME_TYPE_GPS, payload)

    def send_attitude(self, pitch_deg, roll_deg, yaw_deg):
        """
        Sends attitude telemetry (Frame 0x1E).
        Args:
            pitch_deg (float): Pitch in degrees
            roll_deg (float): Roll in degrees
            yaw_deg (float): Yaw in degrees
        """
        # Convert to radians * 10000
        pitch = int(pitch_deg * (3.14159 / 180) * 10000)
        roll = int(roll_deg * (3.14159 / 180) * 10000)
        yaw = int(yaw_deg * (3.14159 / 180) * 10000)
        
        payload = s.pack('>hhh', pitch, roll, yaw)
        self._send_packet(FRAME_TYPE_ATTITUDE, payload)

    def send_flight_mode(self, mode_string):
        """
        Sends flight mode telemetry (Frame 0x21).
        Args:
            mode_string (str): A short string (e.g., "ACRO", "STAB")
        """
        # Payload is a null-terminated ASCII string
        payload = mode_string.encode('ascii') + b'\x00'
        self._send_packet(FRAME_TYPE_FLIGHT_MODE, payload)