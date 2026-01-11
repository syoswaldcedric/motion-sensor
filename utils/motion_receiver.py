import threading
import serial.tools.list_ports
import time
import json

# import project metadata
from utils.constants import CONSTANTS


# -----------------------------
# Data acquisition
# -----------------------------
class MotionReceiver(threading.Thread):
    """
    Background thread that listens to the defined serial port and
    pushes motion values to a shared deque.
    """

    def __init__(
        self,
        port,
        baudrate,
        motion_buffer,
        log_buffer,
        transmitter_status,
        use_mock_if_fail=True,
    ):
        super().__init__(daemon=True)
        self.port_name = port
        self.baudrate = baudrate
        self.motion_buffer = motion_buffer
        self.log_buffer = log_buffer
        self.transmitter_status = transmitter_status
        self.use_mock_if_fail = use_mock_if_fail
        self.running = False
        self.serial = None

    def open_port(self):
        # Try the configured port
        try:
            self.serial = serial.Serial(self.port_name, self.baudrate, timeout=1)
            print(f"Established connection with Transmitter at {self.port_name}")
            return True
        except Exception as e:
            msg = f"Host port communication failed: {e}"
            print(msg)
            self.log_buffer.append(msg)

            self.serial = None
            return False

    # DEPRECATED: use parse_transmitter_data instead
    def parse_motion_value(self, raw_line):
        """
        The transmitter sends lines like: 'MOTION:0' or 'MOTION:1'
        """
        try:
            line = raw_line.strip().decode("utf-8")
            print(f"Received: {line}")
            if not line:
                return None
            if "MOTION:" in line:
                _, val = line.split("MOTION:", 1)
                print(f"ExtractedMotion value: {val}")
                return float(val.strip())
            return float(line)
        except Exception:
            return None

    def parse_transmitter_data(self, raw_line):
        """
        The transmitter sends lines like: 'MOTION:0' or 'MOTION:1'
        '{"MOTION": {"value": 1}, "LOG": {"type": "info", "message": "System is on"}}'
        """
        try:
            line = raw_line.strip().decode("utf-8", errors="ignore")

            if not line:
                return None

            json_data = json.loads(line)
            type = json_data.get("type")
            data = json_data.get("data")

            return type, data
        except Exception as e:
            print("Failed to parse transmitter data", e)
            return None

    def mock_motion_value(self):
        """
        Simple motion value mock generator for testing: alternates between 0 and 1.
        """
        import random

        # toggling or random 0/1
        return float(random.randint(0, 1))

    def run(self):
        self.running = True

        if not self.open_port() and not self.use_mock_if_fail:
            return

        while self.running:
            if self.serial:
                try:
                    raw = self.serial.readline()
                    (type, data) = self.parse_transmitter_data(raw)
                    print(type, data)
                    if type == CONSTANTS.get("MESSAGE_TYPES").get("MOTION"):
                        self.motion_buffer.append(data)
                    elif type == CONSTANTS.get("MESSAGE_TYPES").get("LOGS"):
                        self.log_buffer.append(data)
                    elif type == CONSTANTS.get("MESSAGE_TYPES").get(
                        "PERFORMANCE_STATUS"
                    ):
                        self.transmitter_status = data
                except Exception:
                    # fall back to mock data if serial fails mid‑run
                    if self.use_mock_if_fail:
                        self.motion_buffer.append(self.mock_motion_value())
            else:
                # mock mode
                self.motion_buffer.append(self.mock_motion_value())

            time.sleep(0.1)  # Faster acquisition period for responsiveness

    def stop(self):
        self.running = False
        try:
            if self.serial and self.serial.is_open:
                self.serial.close()
        except Exception:
            pass
