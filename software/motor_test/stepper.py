from machine import Pin, Timer

class Stepper:
    def __init__(self, step_pin, dir_pin, steps_per_revolution=200):
        """
        Initialize the Stepper class.

        :param step_pin: GPIO pin number for the STEP signal
        :param dir_pin: GPIO pin number for the DIR signal
        :param steps_per_revolution: Total steps per revolution (default: 3200 for 1/16 microstepping)
        """
        self.step_pin = Pin(step_pin, Pin.OUT)
        self.dir_pin = Pin(dir_pin, Pin.OUT)
        self.steps_per_revolution = steps_per_revolution

        self.step_count = 0
        self.target_steps = 0
        self.direction = 1

        self.timer = Timer()

    def _step_motor(self, timer):
        """Timer callback to generate a step pulse."""
        if self.step_count < self.target_steps:
            self.step_pin.value(1)
            self.step_pin.value(0)  # Generate a short pulse
            self.step_count += 1
        else:
            self.timer.deinit()  # Stop the timer

    def move(self, rpm, rotations, direction):
        """
        Move the motor at a specified RPM for a given number of rotations in a specified direction.

        :param rpm: Speed in RPM
        :param rotations: Number of rotations to complete
        :param direction: 1 for CW, 0 for CCW
        """
        self.dir_pin.value(direction)
        self.direction = direction

        # Calculate total steps and step interval
        self.target_steps = int(rotations * self.steps_per_revolution)
        step_interval_us = int(1e6 * (60 / (self.steps_per_revolution * rpm)))

        # Reset step count and start the timer
        self.step_count = 0
        self.timer.init(freq=int(1e6 / step_interval_us), mode=Timer.PERIODIC, callback=self._step_motor)

    def stop(self):
        """Stop the motor immediately."""
        self.timer.deinit()
        self.target_steps = 0

    def get_rotation(self):
        """
        Get the current rotation of the motor in degrees.

        :return: Rotation in degrees
        """
        return (self.step_count / self.steps_per_revolution) * 360

# Example Usage
if __name__ == "__main__":
    # Initialize the stepper motor (STEP on GPIO 16, DIR on GPIO 17)
    stepper = Stepper(step_pin=17, dir_pin=16)

    # Move the motor: 5 RPM, 2 rotations, clockwise
    stepper.move(rpm=5, rotations=5, direction=1)

    # Wait for completion
    while stepper.step_count < stepper.target_steps:
        pass

    print(f"Motor rotated {stepper.get_rotation()} degrees.")

    # Stop the motor (optional, as it stops automatically after reaching target steps)
    stepper.stop()
