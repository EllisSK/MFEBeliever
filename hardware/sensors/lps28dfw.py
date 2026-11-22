import struct as s


class LPS28DFW:
    WHO_AM_I = 0x0F
    CTRL_REG1 = 0x10
    CTRL_REG2 = 0x11
    CTRL_REG3 = 0x12
    STATUS = 0x27
    PRESS_OUT_XL = 0x28

    def __init__(self, i2c, address=0x5C):
        self._i2c = i2c
        self._address = address
        if i2c.readfrom_mem(address, self.WHO_AM_I, 1) != b"\xb4":
            raise OSError("LPS28DFW not found")

        i2c.writeto_mem(address, self.CTRL_REG2, b"\x08")  # BDU, 1260 hPa
        i2c.writeto_mem(address, self.CTRL_REG3, b"\x01")  # Auto-increment
        i2c.writeto_mem(address, self.CTRL_REG1, b"\x1a")  # 10 Hz, 16 samples

    def read(self):
        """Return pressure in hPa and temperature in Celsius when ready."""
        status = self._i2c.readfrom_mem(self._address, self.STATUS, 1)[0]
        if status & 0x03 != 0x03:
            return None

        data = self._i2c.readfrom_mem(self._address, self.PRESS_OUT_XL, 5)
        pressure = (data[2] << 16) | (data[1] << 8) | data[0]
        if pressure & 0x800000:
            pressure -= 0x1000000
        temperature = s.unpack("<h", data[3:])[0]
        return pressure / 4096, temperature / 100
