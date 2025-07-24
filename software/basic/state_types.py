from enum import Enum, auto

class ArmState(Enum):
    DISARMED = auto()
    ARMED = auto()

class FlightState(Enum):
    GROUNDED = auto()
    MANNED = auto()
    UNMANNED = auto()

class ConnectionState(Enum):
    CONNECTED = auto()
    DISCONNECTED = auto()