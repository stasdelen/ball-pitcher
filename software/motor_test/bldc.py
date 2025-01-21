import time
from machine import Pin, PWM

class ESC:
    def __init__(self, pwm_pin, freq=50, min_throttle=1000, max_throttle=2000):
        """
        Initialize the ESC class.

        :param pwm_pin: GPIO pin number for the PWM signal
        :param freq: PWM frequency in Hz (default: 50 Hz for most ESCs)
        :param min_throttle: Minimum throttle value (default: 1000)
        :param max_throttle: Maximum throttle value (default: 2000)
        """
        self.pwm = PWM(Pin(pwm_pin))
        self.pwm.freq(freq)

        self.min_throttle = min_throttle
        self.max_throttle = max_throttle

        # Initialize ESC at minimum throttle
        self.set_throttle(self.min_throttle)

    def _throttle_to_duty(self, throttle):
        """
        Convert throttle value to a duty cycle.

        :param throttle: Throttle value between min_throttle and max_throttle
        :return: Duty cycle as an integer
        """
        pulse_width = throttle / 1e6  # Convert throttle to seconds (e.g., 1500 -> 0.0015)
        duty = int(pulse_width * self.pwm.freq() * 65535)
        return duty

    def set_throttle(self, throttle):
        """
        Set the ESC throttle.

        :param throttle: Throttle value between min_throttle and max_throttle
        """
        if throttle < self.min_throttle or throttle > self.max_throttle:
            raise ValueError(f"Throttle must be between {self.min_throttle} and {self.max_throttle}.")

        duty = self._throttle_to_duty(throttle)
        self.pwm.duty_u16(duty)

    def stop(self):
        """Stop the ESC by setting throttle to minimum."""
        self.set_throttle(self.min_throttle)

    def deinit(self):
        """Stop the PWM signal to the ESC."""
        self.pwm.deinit()

# CLI for controlling ESCs
def main():
    esc1 = ESC(pwm_pin=18)
    esc2 = ESC(pwm_pin=19)
    esc3 = ESC(pwm_pin=20)

    print("ESC CLI initialized. Type 'help' for commands.")

    try:
        while True:
            command = input("Enter command (e.g., 'set 1 1500', 'stop', 'exit'): ")

            if command.startswith("set"):
                # Parse the command
                parts = command.split()
                if len(parts) == 3:
                    esc_number = int(parts[1])
                    throttle = int(parts[2])

                    if esc_number == 1:
                        esc1.set_throttle(throttle)
                    elif esc_number == 2:
                        esc2.set_throttle(throttle)
                    elif esc_number == 3:
                        esc3.set_throttle(throttle)
                    else:
                        print("Invalid ESC number. Use 1, 2, or 3.")
                else:
                    print("Invalid command format. Use 'set <esc_number> <throttle>'.")

            elif command == "stop":
                esc1.stop()
                esc2.stop()
                esc3.stop()
                print("All ESCs stopped.")

            elif command == "exit":
                print("Exiting CLI and deinitializing ESCs...")
                esc1.deinit()
                esc2.deinit()
                esc3.deinit()
                break

            elif command == "help":
                print("""
Available commands:
- set <esc_number> <throttle>: Set throttle value for a specific ESC (e.g., 'set 1 1500').
- stop: Stop all ESCs.
- exit: Exit the program and deinitialize ESCs.
- help: Show this help message.
                """)

            else:
                print("Unknown command. Type 'help' for available commands.")

    except KeyboardInterrupt:
        print("\nExiting CLI and deinitializing ESCs...")
        esc1.deinit()
        esc2.deinit()
        esc3.deinit()

if __name__ == "__main__":
    main()
