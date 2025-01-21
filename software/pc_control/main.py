import math
import time
import random
from bldc import ESC
from servo import Servo
from stepper import Stepper


class TennisBallPitcherCLI:
    def __init__(self):
        # Initialize motors
        self.esc1 = ESC(pwm_pin=18)  # Bottom BLDC motor
        self.esc2 = ESC(pwm_pin=19)  # Right-Top BLDC motor
        self.esc3 = ESC(pwm_pin=20)  # Left-Top BLDC motor
        self.pitch_servo = Servo(pwm_pin=15, gear_ratio=86 / 26, angle_shift=90, angle_range=70)
        self.yaw_servo = Servo(pwm_pin=14, gear_ratio=2 / 1, angle_shift=90, angle_range=90)
        self.stepper_motor = Stepper(step_pin=17, dir_pin=16)

        # Store throw settings
        self.throw_settings = {
            "base_speed": 0,    # Base speed in RPM
            "spin_effect": 0,   # Spin effect in RPM
            "spin_angle": 0     # Spin angle in degrees
        }
        print("Tennis Ball Pitcher CLI initialized. Type 'help' for commands.")

    @staticmethod
    def calculate_motor_speeds(base_speed, spin_effect, spin_angle):
        """Calculate motor RPMs based on the given parameters."""
        # Convert angles to radians
        spin_angle_rad = math.radians(spin_angle)
        motor_bottom_angle = math.radians(270)
        motor_right_top_angle = math.radians(30)
        motor_left_top_angle = math.radians(150)

        # Compute RPMs for each motor
        rpm_bottom = base_speed + spin_effect * math.cos(spin_angle_rad - motor_bottom_angle)
        rpm_right_top = base_speed + spin_effect * math.cos(spin_angle_rad - motor_right_top_angle)
        rpm_left_top = base_speed + spin_effect * math.cos(spin_angle_rad - motor_left_top_angle)

        return int(rpm_bottom), int(rpm_right_top), int(rpm_left_top)

    def set_throw(self, base_speed, spin_effect, spin_angle):
        """Set throw parameters."""
        self.throw_settings["base_speed"] = base_speed
        self.throw_settings["spin_effect"] = spin_effect
        self.throw_settings["spin_angle"] = spin_angle
        print(f"Throw settings updated: Base Speed={base_speed} RPM, Spin Effect={spin_effect} RPM, "
              f"Spin Angle={spin_angle}°.")

    def set_angle(self, pitch, yaw):
        """Set pitch and yaw angles."""
        self.pitch_servo.set_angle(-pitch)
        self.yaw_servo.set_angle(yaw)
        print(f"Pitch set to {pitch}°, Yaw set to {yaw}°.")

    def home(self):
        """Send pitch and yaw to zero degrees."""
        self.pitch_servo.set_angle(0)
        self.yaw_servo.set_angle(0)
        print("Servos homed to 0° for both pitch and yaw.")

    def shoot(self, num_balls, feed_bpm):
        """Shoot balls using BLDC motors and stepper motor."""
        print(f"Shooting {num_balls} balls at feed rate {feed_bpm} BPM...")

        # Calculate motor RPMs
        base_speed = self.throw_settings["base_speed"]
        spin_effect = self.throw_settings["spin_effect"]
        spin_angle = self.throw_settings["spin_angle"]
        rpm_bottom, rpm_right_top, rpm_left_top = self.calculate_motor_speeds(base_speed, spin_effect, spin_angle)

        # Set motor speeds
        self.esc1.set_throttle(rpm_bottom)
        self.esc2.set_throttle(rpm_right_top)
        self.esc3.set_throttle(rpm_left_top)
        print(f"Motors set: Bottom={rpm_bottom} RPM, Right-Top={rpm_right_top} RPM, Left-Top={rpm_left_top} RPM.")

        # Calculate stepper motor RPM from feed BPM
        stepper_rpm = feed_bpm / 6  # Convert feed rate to stepper RPM
        feed_time = 60 / feed_bpm  # Time between feeding balls (in seconds)

        # Feed balls using the stepper motor
        for i in range(num_balls):
            self.stepper_motor.move(rpm=stepper_rpm, rotations=1 / 6, direction=1)
            time.sleep(feed_time)  # Pause between balls
        print(f"{num_balls} balls shot successfully.")

        # Stop motors after shooting
        self.stop_motors()

    def stepper(self, angle, rpm=120):
        """Manually move the stepper motor to a specific angle with a given RPM."""
        rotations = abs(angle) / 360  # Convert angle to rotations
        direction = 1 if angle > 0 else 0  # CW if positive, CCW if negative
        self.stepper_motor.move(rpm=rpm, rotations=rotations, direction=direction)
        print(f"Stepper motor moved {angle}° at {rpm} RPM ({'CW' if direction == 1 else 'CCW'}).")

    def stop_motors(self):
        """Stop all motors."""
        self.esc1.stop()
        self.esc2.stop()
        self.esc3.stop()
        self.stepper_motor.stop()
        print("All motors stopped.")

    def random_mode(self, feed_bpm, max_throw_speed, max_spin, max_pitch, max_yaw, num_balls):
        """Activate random mode for shooting balls."""
        print("Starting random mode...")
        print(f"Feed Rate: {feed_bpm} BPM, Max Throw Speed: {max_throw_speed} RPM, "
              f"Max Spin: {max_spin} RPM, Max Pitch: {max_pitch}°, Max Yaw: {max_yaw}°.")

        stepper_rpm = feed_bpm / 6  # Convert feed rate to stepper RPM
        feed_time = 60 / feed_bpm  # Time between feeding balls (in seconds)

        for i in range(num_balls):
            # Randomize throw parameters
            throw_speed = random.randint(1000, max_throw_speed)  # Random base RPM
            spin_effect = random.randint(-max_spin, max_spin)  # Random spin RPM
            spin_angle = random.uniform(0, 360)  # Random spin angle in degrees
            pitch_angle = random.uniform(-max_pitch, max_pitch)  # Random pitch angle
            yaw_angle = random.uniform(-max_yaw, max_yaw)  # Random yaw angle

            # Set pitch and yaw
            self.pitch_servo.set_angle(pitch_angle)
            self.yaw_servo.set_angle(yaw_angle)
            print(f"Ball {i + 1}: Pitch={pitch_angle}°, Yaw={yaw_angle}°, "
                  f"Speed={throw_speed} RPM, Spin={spin_effect} RPM, Spin Angle={spin_angle}°.")

            # Calculate motor RPMs
            rpm_bottom, rpm_right_top, rpm_left_top = self.calculate_motor_speeds(throw_speed, spin_effect, spin_angle)

            # Set motor speeds
            self.esc1.set_throttle(rpm_bottom)
            self.esc2.set_throttle(rpm_right_top)
            self.esc3.set_throttle(rpm_left_top)

            # Feed the ball
            self.stepper_motor.move(rpm=stepper_rpm, rotations=1 / 6, direction=1)
            time.sleep(feed_time)  # Pause between balls

        # Stop all motors after shooting
        self.stop_motors()
        print("Random mode complete. All motors stopped.")


    def run(self):
        """CLI main loop."""
        try:
            while True:
                command = input("Enter command: ").strip()

                if command.startswith("set_throw"):
                    # Format: set_throw <base_speed> <spin_effect> <spin_angle>
                    parts = command.split()
                    if len(parts) == 4:
                        base_speed = int(parts[1])
                        spin_effect = int(parts[2])
                        spin_angle = float(parts[3])
                        self.set_throw(base_speed, spin_effect, spin_angle)
                    else:
                        print("Invalid command. Format: set_throw <base_speed> <spin_effect> <spin_angle>")

                elif command.startswith("set_angle"):
                    # Format: set_angle <pitch> <yaw>
                    parts = command.split()
                    if len(parts) == 3:
                        pitch = float(parts[1])
                        yaw = float(parts[2])
                        self.set_angle(pitch, yaw)
                    else:
                        print("Invalid command. Format: set_angle <pitch> <yaw>")

                elif command == "home":
                    self.home()

                elif command.startswith("shoot"):
                    # Format: shoot <number_of_balls> <feed_bpm>
                    parts = command.split()
                    if len(parts) == 3:
                        num_balls = int(parts[1])
                        feed_bpm = int(parts[2])
                        self.shoot(num_balls, feed_bpm)
                    else:
                        print("Invalid command. Format: shoot <number_of_balls> <feed_bpm>")

                elif command.startswith("stepper"):
                    # Format: stepper <angle> [rpm]
                    parts = command.split()
                    if len(parts) == 2 or len(parts) == 3:
                        angle = float(parts[1])
                        rpm = int(parts[2]) if len(parts) == 3 else 120
                        self.stepper(angle, rpm)
                    else:
                        print("Invalid command. Format: stepper <angle> [rpm]")

                elif command.startswith("random_mode"):
                    # Format: random_mode <feed_bpm> <max_throw_speed> <max_spin> <max_pitch> <max_yaw> <num_balls>
                    parts = command.split()
                    if len(parts) == 7:
                        feed_bpm = int(parts[1])
                        max_throw_speed = int(parts[2])
                        max_spin = int(parts[3])
                        max_pitch = float(parts[4])
                        max_yaw = float(parts[5])
                        num_balls = int(parts[6])
                        self.random_mode(feed_bpm, max_throw_speed, max_spin, max_pitch, max_yaw, num_balls)
                    else:
                        print("Invalid command. Format: random_mode <feed_bpm> <max_throw_speed> <max_spin> "
                              "<max_pitch> <max_yaw> <num_balls>")

                elif command == "stop":
                    self.stop_motors()

                elif command == "help":
                    print("""
Available commands:
- set_throw <base_speed> <spin_effect> <spin_angle>: Save throw settings (e.g., 'set_throw 1500 500 45').
- set_angle <pitch> <yaw>: Set pitch and yaw angles for targeting (e.g., 'set_angle 30 45').
- home: Reset pitch and yaw angles to 0°.
- shoot <number_of_balls> <feed_bpm>: Shoot balls at the specified feed rate (e.g., 'shoot 5 90').
- stepper <angle> [rpm]: Manually rotate the stepper motor by a specific angle at a given RPM (e.g., 'stepper 90 100').
- random_mode <feed_bpm> <max_throw_speed> <max_spin> <max_pitch> <max_yaw> <num_balls>: 
  Activates random mode for throwing balls with randomized settings.
- stop: Stop all motors.
- help: Show this help message.
                    """)

                elif command == "exit":
                    print("Exiting and deinitializing motors...")
                    self.stop_motors()
                    self.pitch_servo.deinit()
                    self.yaw_servo.deinit()
                    break

                else:
                    print("Unknown command. Type 'help' for available commands.")

        except KeyboardInterrupt:
            print("\nExiting and deinitializing motors...")
            self.stop_motors()
            self.pitch_servo.deinit()
            self.yaw_servo.deinit()


if __name__ == "__main__":
    cli = TennisBallPitcherCLI()
    cli.run()
