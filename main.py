import machine as m
import utime as t
import _thread as mt

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

from software import (
    ArmState,
    FlightState,
    ConnectionState
)

#Enter calibration values below:~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TRANSCEIVER_UART_ID = None
TRANSCEIVER_TX_PIN = None
TRANSCEIVER_RX_PIN = None
LEFT_ESC_PIN = None
RIGHT_ESC_PIN = None
LEFT_AILERON_PIN = None
RIGHT_AILERON_PIN = None
LEFT_RUDDERVATOR_PIN = None
RIGHT_RUDDERVATOR_PIN = None
PARACHUTE_PIN = None
V_SENS_PIN = None
I_SENS_PIN = None
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Initialising basic hardware::~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
transceiver = SpeedyBeeNanoELRS(
    uart_id=TRANSCEIVER_UART_ID,
    tx_pin=TRANSCEIVER_TX_PIN,
    rx_pin=TRANSCEIVER_RX_PIN
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
power_module = HolybroPM02v3(
    v_sens = V_SENS_PIN,
    i_sens = I_SENS_PIN
)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Initialising sensor hardware:~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
imu = ICM20948(
    
)
gnss = UbloxNeoM9N(

)
barometer = LPS28DFW(

)
ultrasonic = HCSR04(

)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Initialising state variables:~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
isArmed = ArmState.DISARMED
isConnected = ConnectionState.DISCONNECTED
flightMode = FlightState.GROUNDED
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Main loop:~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
while True:
    pass
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~