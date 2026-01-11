import RPi.GPIO as GPIO
import serial
import time
import datetime
import psutil
import json

# Serial setup
ser = serial.Serial("/dev/ttyAMA0", 9600, timeout=1)

INPUT_PIN = 17
MESSAGE_TYPES = {
    "MOTION": "MOTION",
    "LOGS": "LOGS",
    "PERFORMANCE_STATUS": "PERFORMANCE_STATUS",
}


class PiSender:
    def __init__(self):
        self.initialize_gpio()
        self.send_perf_status()

    def initialize_gpio(self):
        # GPIO setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(INPUT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        print("Initializing GPIO pins.............................")
        time.sleep(10)  # give module time to initialize

    def send_message(self, type, msg):
        data = {"type": type, "data": msg}
        str_data = json.dumps(data)
        ser.write(str_data.encode("utf-8") + b"\n")
        print(f"Sent: {str_data}")

    def read_message(self):
        line = ser.readline()
        if line:
            return line.decode("utf-8").strip()
        return None

    def send_perf_status(self):
        # simple network throughput estimation (kB/s)
        net1 = psutil.net_io_counters()
        time.sleep(0.1)
        net2 = psutil.net_io_counters()
        sent_kbps = (net2.bytes_sent - net1.bytes_sent) / 1024.0 / 0.1
        recv_kbps = (net2.bytes_recv - net1.bytes_recv) / 1024.0 / 0.1
        data = {
            "type": MESSAGE_TYPES.get("PERFORMANCE_STATUS"),
            "data": {
                "cpu": psutil.cpu_percent(interval=1),
                "memory": psutil.virtual_memory().percent,
                "disk": psutil.disk_usage("/").percent,
                "net_up": sent_kbps,
                "net_down": recv_kbps,
                "timestamp": datetime.now(),
                "version": "Raspberypi 1b+ v1.2",
            },
        }
        str_data = json.dumps(data)
        print(str_data)
        self.send_message(MESSAGE_TYPES.get("PERFORMANCE_STATUS"), str_data)

    def run(self):
        try:
            while True:
                # Send a test message
                sensor_value = GPIO.input(INPUT_PIN)
                message = f"MOTION: {sensor_value}"
                if sensor_value == 1:
                    self.send_message(MESSAGE_TYPES.get("MOTION"), message)
                    time.sleep(3)
                else:
                    self.send_message(MESSAGE_TYPES.get("MOTION"), message)
                    time.sleep(0.5)

                # Read incoming message (if any)
                incoming = self.read_message()
                if incoming:
                    print(f"Received: {incoming}")

        except KeyboardInterrupt:
            print("Exiting Pi A...")
            ser.close()


if __name__ == "__main__":
    print("Pi A running (Coordinator)")
    pi_sender = PiSender()
    pi_sender.run()
