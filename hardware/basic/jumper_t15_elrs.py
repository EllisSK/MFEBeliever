import machine as m
import utime as t
from speedybee_nano_elrs import SpeedyBeeNanoELRS

class JumperT15(SpeedyBeeNanoELRS):
    def __init__(self, chip: int, tx_pin: int, rx_pin: int):
        super().__init__(
            chip=chip,
            tx_pin=tx_pin,
            rx_pin=rx_pin
        )