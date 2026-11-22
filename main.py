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
from hardware.basic.speedybee_nano_elrs import STATUS_WARNING
from software.basic.telemetry import Telemetry


TRANSCEIVER_UART = None  # (id, tx, rx)
GNSS_UART = None         # (id, tx, rx)
SENSOR_I2C = None        # (id, scl, sda)
IMU_ADDRESS = 0x68
BAROMETER_ADDRESS = 0x5C
POWER_PINS = None        # (voltage, current)
BATTERY_WARNING_V = None
BATTERY_CAPACITY_MAH = None
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

    telemetry = Telemetry(None, BATTERY_WARNING_V, BATTERY_CAPACITY_MAH)
    if TRANSCEIVER_UART:
        telemetry.radio = telemetry.read("Radio UART", SpeedyBeeNanoELRS, *TRANSCEIVER_UART)

    gnss = telemetry.read("GPS", UbloxNeoM9N, *GNSS_UART) if GNSS_UART else None
    if gnss is not None:
        telemetry.notify("Waiting for GPS fix")
    power = telemetry.read("Power monitor", HolybroPM02v3, *POWER_PINS) if POWER_PINS else None
    ultrasonic = telemetry.read("Rangefinder", HCSR04, *ULTRASONIC_PINS) if ULTRASONIC_PINS else None
    imu = None
    barometer = None
    if SENSOR_I2C:
        bus, scl, sda = SENSOR_I2C
        i2c = telemetry.read("Sensor bus", m.I2C, bus, scl=m.Pin(scl), sda=m.Pin(sda), freq=400_000)
        if i2c is not None and IMU_ADDRESS is not None:
            imu = telemetry.read("IMU", ICM20948, i2c, IMU_ADDRESS)
        if i2c is not None and BAROMETER_ADDRESS is not None:
            barometer = telemetry.read("Barometer", LPS28DFW, i2c, BAROMETER_ADDRESS)

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
                try:
                    outputs.append(driver(pin))
                except (OSError, ValueError):
                    telemetry.guide(f"PWM setup failed on pin {pin}", STATUS_WARNING)
                    raise

        if not (outputs or telemetry.radio or gnss or power or ultrasonic or imu or barometer):
            if TRANSCEIVER_UART or GNSS_UART or POWER_PINS or ULTRASONIC_PINS or SENSOR_I2C:
                print("No configured devices are available.")
            else:
                print("Configure hardware in main.py.")
            return

        last_report = t.ticks_ms()
        while True:
            telemetry.update()
            if gnss is not None:
                telemetry.read("GPS", gnss.update)

            now = t.ticks_ms()
            if t.ticks_diff(now, last_report) >= 1000:
                last_report = now
                fix = gnss.get_fix() if gnss is not None else None
                battery = telemetry.read("Power monitor", power.read) if power is not None else None
                pressure = (
                    telemetry.read("Barometer", barometer.read)
                    if barometer is not None else None
                )
                readings = {}
                if telemetry.radio is not None:
                    readings["rc_connected"] = telemetry.connected
                if gnss is not None:
                    readings["gps_fix"] = fix
                if battery is not None:
                    readings["battery_v"], readings["battery_a"] = battery
                if imu is not None:
                    readings["imu"] = telemetry.read("IMU", imu.read_motion)
                    readings["magnetic_ut"] = telemetry.read("Magnetometer", imu.read_magnetic_ut)
                if barometer is not None:
                    readings["barometer"] = pressure
                if ultrasonic is not None:
                    readings["distance_cm"] = telemetry.read("Rangefinder", ultrasonic.read_distance_cm)
                telemetry.publish(now, fix, battery, pressure)
                if readings:
                    print(readings)
            t.sleep_ms(2)
    finally:
        for output in outputs:
            output.deinit()


def calibrate_esc(side):
    if side == "left":
        pin = LEFT_ESC_PIN
    elif side == "right":
        pin = RIGHT_ESC_PIN
    else:
        raise ValueError("Select the left or right ESC")
    if pin is None:
        raise ValueError("Configure the selected ESC pin in main.py")

    telemetry = Telemetry(None)
    if TRANSCEIVER_UART:
        telemetry.radio = telemetry.read("Radio UART", SpeedyBeeNanoELRS, *TRANSCEIVER_UART)
    esc = None
    try:
        esc = HobbywingXRotorPro(pin)
        if telemetry.radio is not None:
            telemetry.send(telemetry.radio.send_flight_mode, "ESC CAL")
        esc.calibrate(telemetry.guide)
    except (EOFError, KeyboardInterrupt):
        telemetry.guide(f"{side.capitalize()} ESC calibration cancelled", STATUS_WARNING)
        raise
    except (OSError, ValueError):
        telemetry.guide(f"{side.capitalize()} ESC calibration failed", STATUS_WARNING)
        raise
    finally:
        if esc is not None:
            esc.deinit()
        if telemetry.radio is not None:
            telemetry.send(telemetry.radio.send_flight_mode, "GROUND")


if __name__ == "__main__":
    run()
