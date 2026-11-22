try:
    from enum import Enum
except ImportError:
    class _State:
        def __init__(self, name, value):
            self.name = name
            self.value = value

    def Enum(name, members):
        values = {
            member: _State(member, value)
            for value, member in enumerate(members, 1)
        }
        return type(name, (), values)


ArmState = Enum("ArmState", ("DISARMED", "ARMED"))
FlightState = Enum("FlightState", ("GROUNDED", "MANNED", "UNMANNED"))
ConnectionState = Enum("ConnectionState", ("CONNECTED", "DISCONNECTED"))
