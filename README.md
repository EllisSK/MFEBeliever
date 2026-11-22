# MFE Believer Fixed Wing UAV Project

![MFE Believer UAV](https://en.makeflyeasy.com/wp-content/uploads/2021/09/%E4%BA%A7%E5%93%817.png)

## Description:
This repository contains micropython code required to operate the MFE believer UAV with the hardware specified below. Code handling hardware components is stored within the hardware directory, whilst any advanced software features (such as an autopilot) will be stored in the software directory.

## Usage:
Set the pin and bus assignments at the top of `main.py` and copy the project to the RP2350 MicroPython filesystem. Leave unused devices set to `None`. The receiver and GNSS need separate UARTs. The IMU and barometer can share an I²C bus.

At startup, the program polls the configured receiver and sensors and prints readings once a second. The ESCs receive minimum throttle and the servos start with PWM duty set to zero. Feed the HC-SR04 echo pin through a 3.3 V-compatible signal path.

With ExpressLRS telemetry enabled, discover the battery, GPS, barometric altitude, and flight-mode sensors in EdgeTX. Barometric altitude is relative to the first valid pressure reading after startup. Set `BATTERY_WARNING_V` to the minimum pack voltage for low-voltage warnings. Set `BATTERY_CAPACITY_MAH` for an estimated remaining percentage, which assumes a full pack at startup.

Run the Yaapu widget with CRSF passthrough enabled on the T15 to display status text. Warnings also appear in the console. A lost-link warning can reach the handset after the link returns. [Yaapu setup](https://github.com/yaapu/FrskyTelemetryScript/wiki/Passthrough-over-CRSF-and-ExpressLRS)

For ESC calibration, stop the monitor with Ctrl+C and run this from the MicroPython console.

```python
import main
main.calibrate_esc("left")
```

Use `"right"` for the other ESC. Calibration prompts appear in the console and are mirrored to the handset. Confirm the steps at the console.

## Main Hardware:
* SparkFun Thing Plus - RP2350
* 2x Hobbywing X-Rotor Pro 50A ESC
* 4x Emax ES3504 Servos
* Emax ES08MD-II Servo
* SpeedyBee Nano ELRS Transceiver
* Holybro PM02 V3 Power Module

## Other Hardware:
* TBD

## Contributing:
This project is closed to contributions.
