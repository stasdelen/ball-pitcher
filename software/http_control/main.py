import network
import socket
import math
import time
import random
from bldc import ESC
from servo import Servo
from stepper import Stepper


class TennisBallPitcherHTTP:
    def __init__(self):
        # Initialize motors
        self.esc1 = ESC(pwm_pin=18)
        self.esc2 = ESC(pwm_pin=19)
        self.esc3 = ESC(pwm_pin=20)
        self.pitch_servo = Servo(pwm_pin=15, gear_ratio=86 / 26, angle_shift=90, angle_range=70)
        self.yaw_servo = Servo(pwm_pin=14, gear_ratio=2 / 1, angle_shift=90, angle_range=90)
        self.stepper_motor = Stepper(step_pin=17, dir_pin=16)

        # Stored configuration
        self.config = {
            "speed": 0,
            "frequency": 0,
            "yaw": 0,
            "pitch": 0,
            "spin": 0,
            "spin_angle": 0,
        }

    def stop_all_motors(self):
        """Stop all motors."""
        self.esc1.stop()
        self.esc2.stop()
        self.esc3.stop()
        self.stepper_motor.stop()
        return "All motors stopped."

    def send(self, speed, frequency, yaw, pitch, spin, spin_angle):
        """Save configuration for shooting."""
        self.config.update({
            "speed": speed,
            "frequency": frequency,
            "yaw": yaw,
            "pitch": pitch,
            "spin": spin,
            "spin_angle": spin_angle,
        })
        return f"Configuration saved: Speed={speed}, Frequency={frequency}, Yaw={yaw}, Pitch={pitch}, Spin={spin}, Spin Angle={spin_angle}"

    def shoot(self, num_balls):
        """Shoot balls using the saved configuration."""
        speed = self.config["speed"]
        frequency = self.config["frequency"]
        yaw = self.config["yaw"]
        pitch = self.config["pitch"]
        spin = self.config["spin"]
        spin_angle = self.config["spin_angle"]

        # Set yaw and pitch
        self.pitch_servo.set_angle(-pitch)
        self.yaw_servo.set_angle(yaw)

        # Calculate motor speeds for spin effect
        spin_angle_rad = math.radians(spin_angle)
        bottom_speed = speed + spin * math.cos(spin_angle_rad - math.radians(270))
        right_top_speed = speed + spin * math.cos(spin_angle_rad - math.radians(30))
        left_top_speed = speed + spin * math.cos(spin_angle_rad - math.radians(150))

        # Set motor speeds
        self.esc1.set_throttle(bottom_speed)
        self.esc2.set_throttle(right_top_speed)
        self.esc3.set_throttle(left_top_speed)

        # Simulate ball shooting
        feed_time = 60 / frequency
        for _ in range(num_balls):
            self.stepper_motor.move(rpm=frequency / 6, rotations=1 / 6, direction=1)
            time.sleep(feed_time)

        self.stop_all_motors()
        return f"{num_balls} balls shot with saved configuration."

    def random(self, num_balls):
        """Shoot balls with random parameters."""
        for _ in range(num_balls):
            speed = random.randint(1060, 1200)
            frequency = random.randint(5, 20)
            yaw = random.uniform(-25, 25)
            pitch = random.uniform(-15, 15)
            spin = random.randint(-300, 300)
            spin_angle = random.uniform(0, 360)
            self.send(speed, frequency, yaw, pitch, spin, spin_angle)
            self.shoot(1)  # Shoot one ball per random configuration
        return f"Random mode executed: {num_balls} balls shot with random parameters."


# Wi-Fi and HTTP server setup
def start_server():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect("Salih", "wcgw0031")

    while not wlan.isconnected():
        pass

    print("Connected to Wi-Fi:", wlan.ifconfig())

    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    server_socket = socket.socket()
    server_socket.bind(addr)
    server_socket.listen(5)
    print("Listening on:", addr)

    pitcher = TennisBallPitcherHTTP()

    while True:
        client_socket, client_address = server_socket.accept()
        request = client_socket.recv(1024).decode("utf-8")
        print("Request:", request)

        # Parse the request
        request_line = request.split("\r\n")[0]
        method, path, _ = request_line.split(" ")
        response = "Invalid command"

        if method == "GET":
            query = path[2:]  # Remove "/?"
            command, *params = query.split(",")

            try:
                if command == "send":
                    response = pitcher.send(
                        int(params[0]), int(params[1]), int(params[2]),
                        int(params[3]), int(params[4]), int(params[5])
                    )
                elif command == "shoot":
                    response = pitcher.shoot(int(params[0]))
                elif command == "random":
                    response = pitcher.random(int(params[0]))
                elif command == "off":
                    response = pitcher.stop_all_motors()
                else:
                    response = "Unknown command"
            except Exception as e:
                response = f"Error processing command: {e}"

        # Send the HTTP response
        print("Response:", response)
        client_socket.send(f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n{response}".encode())
        client_socket.close()


if __name__ == "__main__":
    start_server()
