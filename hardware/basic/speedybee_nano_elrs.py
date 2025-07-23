import machine as m
import utime as t

class SpeedyBeeNanoELRS(m.UART):
    def __init__(self, chip: int, tx_pin: int, rx_pin: int):
        super().__init__(
            id = chip,
            tx=m.Pin(
                    value=tx_pin,
                    mode=m.Pin.OUT
                ),
            rx=m.Pin(
                value=rx_pin,
                mode=m.Pin.IN
                ),
            baudrate=420000
        )