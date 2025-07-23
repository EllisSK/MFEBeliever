import machine as m
import utime as t
import _thread as mt

from hardware import (
    JumperT15,
    HobbywingXRotorPro,
    EmaxES3504,
    EmaxES08MDII,
    HCSR04,
    ICM20948,
    LPS28DFW,
    UbloxNeoM9N
)

"""
This is the main file which will control the drone! 
Other modules should create objects for different sensors and classes with methods for automated flight functions.
This file should contain two loops running simultaneously, one to handle basic flight control and the other to handle autopilot and sensor arithmetic.
"""

#Enter calibration values below:~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
CONTROLLER_UART_CHIP = None
CONTROLLER_TX_PIN = None
CONTROLLER_RX_PIN = None
LEFT_ESC_PIN = None
RIGHT_ESC_PIN = None
LEFT_AILERON_PIN = None
RIGHT_AILERON_PIN = None
LEFT_RUDDERVATOR_PIN = None
RIGHT_RUDDERVATOR_PIN = None
PARACHUTE_PIN = None
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Initialising basic hardware::~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
controller = JumperT15(
    chip=CONTROLLER_UART_CHIP,
    tx_pin=CONTROLLER_TX_PIN,
    rx_pin=CONTROLLER_RX_PIN
)
left_esc = HobbywingXRotorPro(
    pwm_pin=LEFT_ESC_PIN
)
right_esc = HobbywingXRotorPro(
    pwm_pin=RIGHT_ESC_PIN
)
left_aileron = EmaxES3504(
    pwm_pin=LEFT_AILERON_PIN
)
right_aileron = EmaxES3504(
    pwm_pin=RIGHT_AILERON_PIN
)
left_ruddervator = EmaxES3504(
    pwm_pin=LEFT_RUDDERVATOR_PIN
)
right_ruddervator = EmaxES3504(
    pwm_pin=RIGHT_RUDDERVATOR_PIN
)
parachute = EmaxES08MDII(
    pwm_pin=PARACHUTE_PIN
)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Initialising sensor hardware:~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#For future use

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Main loop:~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
while True:
    pass
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~