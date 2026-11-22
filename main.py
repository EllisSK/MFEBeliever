import machine as m
import utime as t

from hardware import (
    SpeedyBeeNanoELRS,
    HobbywingXRotorPro,
    EmaxES3504,
    EmaxES08MDII,
    HolybroPM02v3,
    HCSR04,
    ICM20948,
    LPS28DFW,
    UbloxNeoM9N
)


TRANSCEIVER_UART = None  # (id, tx, rx)
GNSS_UART = None         # (id, tx, rx)
SENSOR_I2C = None        # (id, scl, sda)
IMU_ADDRESS = 0x68
BAROMETER_ADDRESS = 0x5C
POWER_PINS = None        # (voltage, current)
ULTRASONIC_PINS = None   # (trigger, echo)

LEFT_ESC_PIN = None
RIGHT_ESC_PIN = None
LEFT_AILERON_PIN = None
RIGHT_AILERON_PIN = None
LEFT_RUDDERVATOR_PIN = None
RIGHT_RUDDERVATOR_PIN = None
PARACHUTE_PIN = None


def run():
    if TRANSCEIVER_UART and GNSS_UART and TRANSCEIVER_UART[0] == GNSS_UART[0]:
        raise ValueError("The radio and GNSS must use different UARTs")

    radio = SpeedyBeeNanoELRS(*TRANSCEIVER_UART) if TRANSCEIVER_UART else None
    gnss = UbloxNeoM9N(*GNSS_UART) if GNSS_UART else None
    power = HolybroPM02v3(*POWER_PINS) if POWER_PINS else None
    ultrasonic = HCSR04(*ULTRASONIC_PINS) if ULTRASONIC_PINS else None
    imu = None
    barometer = None
    if SENSOR_I2C:
        bus, scl, sda = SENSOR_I2C
        i2c = m.I2C(bus, scl=m.Pin(scl), sda=m.Pin(sda), freq=400_000)
        if IMU_ADDRESS is not None:
            imu = ICM20948(i2c, IMU_ADDRESS)
        if BAROMETER_ADDRESS is not None:
            barometer = LPS28DFW(i2c, BAROMETER_ADDRESS)

    outputs = []
    try:
        for pin, driver in (
            (LEFT_ESC_PIN, HobbywingXRotorPro),
            (RIGHT_ESC_PIN, HobbywingXRotorPro),
            (LEFT_AILERON_PIN, EmaxES3504),
            (RIGHT_AILERON_PIN, EmaxES3504),
            (LEFT_RUDDERVATOR_PIN, EmaxES3504),
            (RIGHT_RUDDERVATOR_PIN, EmaxES3504),
            (PARACHUTE_PIN, EmaxES08MDII)
        ):
            if pin is not None:
                outputs.append(driver(pin))

        if not (outputs or radio or gnss or power or ultrasonic or imu or barometer):
            print("Configure hardware in main.py.")
            return

        last_report = t.ticks_ms()
        while True:
            if radio is not None:
                radio.update()
            if gnss is not None:
                gnss.update()

            now = t.ticks_ms()
            if t.ticks_diff(now, last_report) >= 1000:
                last_report = now
                readings = {}
                if radio is not None:
                    readings["rc_connected"] = radio.is_connected()
                if gnss is not None:
                    readings["gps_fix"] = gnss.get_fix()
                if power is not None:
                    readings["battery_v"] = power.read_voltage()
                    readings["battery_a"] = power.read_current()
                if imu is not None:
                    readings["imu"] = imu.read_motion()
                    readings["magnetic_ut"] = imu.read_magnetic_ut()
                if barometer is not None:
                    readings["barometer"] = barometer.read()
                if ultrasonic is not None:
                    readings["distance_cm"] = ultrasonic.read_distance_cm()
                if readings:
                    print(readings)
            t.sleep_ms(2)
    finally:
        for output in outputs:
            output.deinit()


if __name__ == "__main__":
    run()
