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
LEFT_ESC_PIN = None
RIGHT_ESC_PIN = 1
LEFT_AILERON_PIN = None
RIGHT_AILERON_PIN = None
LEFT_RUDDERVATOR_PIN = None
RIGHT_RUDDERVATOR_PIN = None
PARACHUTE_PIN = None
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Initialising basic hardware::~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
controller = JumperT15(

)
left_esc = HobbywingXRotorPro(
    
)
right_esc = HobbywingXRotorPro(

)
left_aileron = EmaxES3504(

)
right_aileron = EmaxES3504(

)
left_ruddervator = EmaxES3504(

)
right_ruddervator = EmaxES3504(

)
parachute = EmaxES08MDII(

)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Initialising sensor hardware::~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#For future use

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~