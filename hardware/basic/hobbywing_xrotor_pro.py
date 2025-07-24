import machine as m
import utime as t

class HobbywingXRotorPro(m.PWM):
    """
    A class to control a Hobbywing X-Rotor Pro ESC (or compatible models)
    using MicroPython's machine.PWM.

    The ESC is controlled by a PWM signal where the pulse width determines the
    motor speed. A standard range is 1000µs for stop and 2000µs for full speed.
    """
    # Standard pulse widths in microseconds (µs)
    MIN_PULSE_WIDTH_US = 1000
    MAX_PULSE_WIDTH_US = 2000

    def __init__(self, pwm_pin: int, freq: int = 50):
        """
        Initializes the ESC controller.

        Args:
            pwm_pin (int): The GPIO pin number connected to the ESC signal wire.
            freq (int): The PWM frequency in Hz. 50Hz is standard for many ESCs,
                        but drone ESCs often support higher frequencies like 400Hz.
        """
        super().__init__(
            m.Pin(pwm_pin),
            freq=freq
        )

        # Calculate the 16-bit duty cycle values corresponding to min/max pulse widths.
        # The period in µs is 1,000,000 / freq.
        period_us = 1_000_000 / freq
        self._min_duty = int((self.MIN_PULSE_WIDTH_US / period_us) * 65535)
        self._max_duty = int((self.MAX_PULSE_WIDTH_US / period_us) * 65535)
        self._duty_range = self._max_duty - self._min_duty

        # Initialize the ESC to a safe (stopped) state.
        self.stop()

    def set_speed(self, speed: float):
        """
        Sets the motor speed as a float from 0.0 (stopped) to 1.0 (full speed).

        Args:
            speed (float): The desired motor speed, from 0.0 to 1.0.
        """
        # Clamp the speed value to the valid range [0.0, 1.0]
        speed = max(0.0, min(1.0, speed))

        # Linearly interpolate the speed to the corresponding duty cycle value
        duty_u16 = self._min_duty + int(speed * self._duty_range)
        self.duty_u16(duty_u16)

    def stop(self):
        """
        Stops the motor by setting the speed to 0.
        """
        self.duty_u16(self._min_duty)

    def arm(self):
        """
        Arms the ESC. This must be done before the motor can run.
        It sends a minimum throttle signal for a few seconds.
        """
        print("Arming ESC: Sending minimum throttle...")
        self.stop()
        t.sleep_ms(2500)
        print("ESC should be armed.")

    def calibrate(self):
        """
        Performs the ESC calibration routine.
        
        ⚠️ IMPORTANT: For this to work, you must:
        1. Disconnect the power from the ESC.
        2. Run this script/method.
        3. When prompted, connect the power to the ESC.
        4. Wait for the beeps to complete.
        """
        print("--- ESC Calibration ---")
        print("1. Ensure propeller is REMOVED and ESC power is OFF.")
        print("2. The throttle will be set to MAX.")
        input("Press Enter to continue...")

        self.set_speed(1.0) # Set max throttle
        print("\n--> NOW, connect power to the ESC.")
        print("--> Wait for the ESC to emit a series of beeps (usually ♪ beep-beep).")
        input("Press Enter after you hear the beeps...")

        self.stop() # Set min throttle
        print("\n--> Throttle set to MIN. The ESC will now confirm.")
        print("--> Wait for a final confirmation beep sequence (e.g., a long beep).")
        t.sleep_ms(3000) # Give time for the ESC to save settings
        print("--- Calibration Complete ---")

    def deinit(self):
        """
        Deinitializes the PWM output, releasing the pin.
        """
        super().deinit()
        print(f"ESC on pin {self.pin} deinitialized.")