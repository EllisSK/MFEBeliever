# MFE Believer Fixed Wing UAV Project

![MFE Believer UAV](https://en.makeflyeasy.com/wp-content/uploads/2021/09/%E4%BA%A7%E5%93%817.png)

## Description:
This repository contains micropython code required to operate the MFE believer UAV with the hardware specified below. Code handling hardware components is stored within the hardware directory, whilst any advanced software features (such as an autopilot) will be stored in the software directory.

## Usage:
Set the pin and bus assignments at the top of `main.py` and copy the project to the RP2350 MicroPython filesystem. Leave unused devices set to `None`. The receiver and GNSS need separate UARTs. The IMU and barometer can share an I²C bus.

At startup, the program polls the configured receiver and sensors and prints readings once a second. The ESCs receive minimum throttle and the servos start with PWM duty set to zero. Feed the HC-SR04 echo pin through a 3.3 V-compatible signal path.

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
