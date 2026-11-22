import struct as s
import utime as t


class ICM20948:
    WHO_AM_I = 0x00
    PWR_MGMT_1 = 0x06
    PWR_MGMT_2 = 0x07
    INT_PIN_CFG = 0x0F
    ACCEL_XOUT_H = 0x2D
    REG_BANK_SEL = 0x7F

    MAG_ADDRESS = 0x0C
    MAG_WIA2 = 0x01
    MAG_ST1 = 0x10
    MAG_CNTL2 = 0x31
    MAG_CNTL3 = 0x32

    def __init__(self, i2c, address=0x68):
        self._i2c = i2c
        self._address = address
        i2c.writeto_mem(address, self.REG_BANK_SEL, b"\x00")
        if i2c.readfrom_mem(address, self.WHO_AM_I, 1) != b"\xea":
            raise OSError("ICM-20948 not found")

        i2c.writeto_mem(address, self.PWR_MGMT_1, b"\x80")
        t.sleep_ms(100)
        i2c.writeto_mem(address, self.PWR_MGMT_1, b"\x01")
        i2c.writeto_mem(address, self.PWR_MGMT_2, b"\x00")
        t.sleep_ms(35)

        i2c.writeto_mem(address, self.INT_PIN_CFG, b"\x02")  # I2C bypass
        if i2c.readfrom_mem(self.MAG_ADDRESS, self.MAG_WIA2, 1) != b"\x09":
            raise OSError("ICM-20948 magnetometer not found")
        i2c.writeto_mem(self.MAG_ADDRESS, self.MAG_CNTL3, b"\x01")
        t.sleep_ms(1)
        i2c.writeto_mem(self.MAG_ADDRESS, self.MAG_CNTL2, b"\x04")  # 20 Hz

    def read_motion(self):
        """Return acceleration in g, rotation in deg/s, and temperature in Celsius."""
        data = self._i2c.readfrom_mem(self._address, self.ACCEL_XOUT_H, 14)
        raw = s.unpack(">7h", data)
        accel = tuple(value / 16384 for value in raw[:3])
        gyro = tuple(value / 131 for value in raw[3:6])
        return accel, gyro, raw[6] / 333.87 + 21

    def read_magnetic_ut(self):
        data = self._i2c.readfrom_mem(self.MAG_ADDRESS, self.MAG_ST1, 9)
        if not data[0] & 0x01 or data[8] & 0x08:
            return None
        return tuple(value * 0.15 for value in s.unpack("<3h", data[1:7]))
