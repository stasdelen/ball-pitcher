import time
from bldc import ESC
from servo import Servo
from stepper import Stepper

def main():
    # Initialize motors
    esc1 = ESC(pwm_pin=18)  # First BLDC motor
    esc2 = ESC(pwm_pin=19)  # Second BLDC motor
    esc3 = ESC(pwm_pin=20)  # Third BLDC motor
    pitch_servo = Servo(pwm_pin=15, gear_ratio=86/26, angle_shift=90, angle_range=70)
    yaw_servo = Servo(pwm_pin=14, gear_ratio=2/1, angle_shift=90, angle_range=90)
    stepper_motor = Stepper(step_pin=17, dir_pin=16)

    print("Tennis Ball Pitcher CLI initialized. Type 'help' for commands.")

    def home_servos():
        """Set yaw and pitch servos to zero degrees."""
        print("Homing servos...")
        pitch_servo.set_angle(0)
        yaw_servo.set_angle(0)
        print("Servos homed to 0 degrees.")

    try:
        while True:
            command = input("Enter command: ").strip()

            if command.startswith("bldc"):
                # Format: bldc <motor_number> <throttle>
                parts = command.split()
                if len(parts) == 3:
                    motor_number = int(parts[1])
                    throttle = int(parts[2])

                    if motor_number == 1:
                        esc1.set_throttle(throttle)
                        print(f"BLDC motor 1 set to throttle {throttle}.")
                    elif motor_number == 2:
                        esc2.set_throttle(throttle)
                        print(f"BLDC motor 2 set to throttle {throttle}.")
                    elif motor_number == 3:
                        esc3.set_throttle(throttle)
                        print(f"BLDC motor 3 set to throttle {throttle}.")
                    else:
                        print("Invalid BLDC motor number. Use 1, 2, or 3.")
                else:
                    print("Invalid command. Format: bldc <motor_number> <throttle>")

            elif command.startswith("stepper"):
                # Format: stepper <rpm> <rotations> <direction>
                parts = command.split()
                if len(parts) == 4:
                    rpm = int(parts[1])
                    rotations = float(parts[2])
                    direction = int(parts[3])

                    if direction not in (0, 1):
                        print("Direction must be 0 (CCW) or 1 (CW).")
                        continue

                    stepper_motor.move(rpm=rpm, rotations=rotations, direction=direction)
                    print(f"Stepper motor moving at {rpm} RPM for {rotations} rotations {'CW' if direction == 1 else 'CCW'}.")
                else:
                    print("Invalid command. Format: stepper <rpm> <rotations> <direction>")

            elif command.startswith("servo"):
                # Format: servo <servo_name> <angle>
                parts = command.split()
                if len(parts) == 3:
                    servo_name = parts[1]
                    angle = float(parts[2])

                    if servo_name == "yaw":
                        yaw_servo.set_angle(angle)
                        print(f"Yaw servo set to {angle} degrees.")
                    elif servo_name == "pitch":
                        pitch_servo.set_angle(angle)
                        print(f"Pitch servo set to {angle} degrees.")
                    else:
                        print("Invalid servo name. Use 'yaw' or 'pitch'.")
                else:
                    print("Invalid command. Format: servo <servo_name> <angle>")

            elif command == "home":
                home_servos()

            elif command == "stop":
                esc1.stop()
                esc2.stop()
                esc3.stop()
                stepper_motor.stop()
                print("All motors stopped.")

            elif command == "exit":
                print("Exiting and deinitializing motors...")
                esc1.deinit()
                esc2.deinit()
                esc3.deinit()
                pitch_servo.deinit()
                yaw_servo.deinit()
                stepper_motor.stop()
                break

            elif command == "help":
                print("""
Available commands:
- bldc <motor_number> <throttle>: Set throttle value for a BLDC motor (e.g., 'bldc 1 1500').
- stepper <rpm> <rotations> <direction>: Move stepper motor at specified RPM, rotations, and direction (e.g., 'stepper 120 5 1').
- servo <servo_name> <angle>: Set servo angle (e.g., 'servo yaw 45').
- home: Home yaw and pitch servos to 0 degrees.
- stop: Stop all motors.
- exit: Exit the program and deinitialize all motors.
- help: Show this help message.
                """)

            else:
                print("Unknown command. Type 'help' for available commands.")

    except KeyboardInterrupt:
        print("\nExiting and deinitializing motors...")
        esc1.deinit()
        esc2.deinit()
        esc3.deinit()
        pitch_servo.deinit()
        yaw_servo.deinit()
        stepper_motor.stop()

if __name__ == "__main__":
    main()
