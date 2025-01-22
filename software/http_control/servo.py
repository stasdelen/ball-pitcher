from machine import Pin, PWM
import time

class Servo:
    def __init__(self, pwm_pin, gear_ratio = 1, angle_shift = 90, angle_range=90, servo_range = 180, freq=50, min_us=500, max_us=2500):
        self.pwm = PWM(Pin(pwm_pin))
        self.pwm.freq(freq)

        self.min_us = min_us
        self.max_us = max_us
        self.gear_ratio = gear_ratio
        self.servo_range = servo_range
        self.absolute_range = angle_range * 2
        self.angle_range = angle_range
        self.angle_shift = angle_shift
        self.angle_min = -angle_range + angle_shift
        self.angle_max = angle_range + angle_shift

    def _angle_to_duty(self, angle):
        pulse_width = self.min_us + (angle / self.servo_range) * (self.max_us - self.min_us)
        duty = int((pulse_width / 1e6) * self.pwm.freq() * 65535)
        return duty

    def set_angle(self, angle):
        angle *= self.gear_ratio
        angle += self.angle_shift
        if angle < self.angle_min or angle > self.angle_max:
            raise ValueError(f"Angle must be between {self.angle_min} and {self.angle_max} degrees.")
        duty = self._angle_to_duty(angle)
        self.pwm.duty_u16(duty)

    def deinit(self):
        self.pwm.deinit()

if __name__ == "__main__":
    pitch_servo = Servo(pwm_pin=14, gear_ratio=86/26, angle_shift=90, angle_range=70)
    yaw_servo = Servo(pwm_pin=15, gear_ratio=2/1, angle_shift=90, angle_range=90)

    for angle in range(-21, 22):
        pitch_servo.set_angle(angle)
        time.sleep(0.2)

    pitch_servo.deinit()

    for angle in range(-45, 45):
        yaw_servo.set_angle(angle)
        time.sleep(0.2)

    pitch_servo.set_angle(0)
    yaw_servo.set_angle(0)


