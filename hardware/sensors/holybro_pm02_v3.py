import machine as m


class HolybroPM02v3:
    def __init__(self, v_sens, i_sens, voltage_divider=18.182,
                 amps_per_volt=36.364, adc_ref=3.3, current_offset_v=0.0):
        self._voltage_adc = m.ADC(m.Pin(v_sens))
        self._current_adc = m.ADC(m.Pin(i_sens))
        self._adc_scale = adc_ref / 65535
        self._voltage_divider = voltage_divider
        self._amps_per_volt = amps_per_volt
        self._current_offset_v = current_offset_v

    def read_voltage(self):
        return self._voltage_adc.read_u16() * self._adc_scale * self._voltage_divider

    def read_current(self):
        voltage = self._current_adc.read_u16() * self._adc_scale
        return max(0.0, voltage - self._current_offset_v) * self._amps_per_volt

    def read(self):
        return self.read_voltage(), self.read_current()
