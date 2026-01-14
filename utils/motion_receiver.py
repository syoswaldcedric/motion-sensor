import threading
import serial.tools.list_ports
import time
import json
from datetime import datetime

# import project metadata
from utils.constants import CONSTANTS
from pathlib import Path

LOG_DIR = Path(CONSTANTS.get("LOG_DIR", Path.cwd()))
date = datetime.now().strftime("%Y-%m-%d")
LOG_FILE = LOG_DIR / date / "motion_log.txt"


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
            self.update_logfile(msg)
            print(msg)
            self.log_buffer.append(msg)

            self.serial = None
            return False



    def update_logfile(self, log):
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a") as f:
            try:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"{timestamp}: {log}\n")
            except Exception as e:
                print(f"Failed to write to log file: {e}")

    def parse_transmitter_data(self, raw_line):
        """
        The transmitter sends lines like: 'MOTION:0' or 'MOTION:1'
        '{"MOTION": {"value": 1}, "LOG": {"type": "info", "message": "System is on"}}'
        """
        try:
            line = raw_line.decode("utf-8", errors="ignore").strip()

            if not line or len(line) < 1:
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
                    (message_type, data) = self.parse_transmitter_data(raw)
                    
                    print(f'type {type}, data: {data}')
                    
                    if data and message_type:
                        if message_type == CONSTANTS.get("MESSAGE_TYPES").get("MOTION", "MOTION"):
                            motion = int(data)
                            self.motion_buffer.append(motion)
                        elif message_type == CONSTANTS.get("MESSAGE_TYPES").get("LOGS", "LOGS"):
                            self.log_buffer.append(data)
                            self.update_logfile(data)
                        elif message_type == CONSTANTS.get("MESSAGE_TYPES").get(
                            "PERFORMANCE_STATUS"
                        ):
                            self.transmitter_status = data
                        else:
                            pass
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
