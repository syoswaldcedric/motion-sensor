import threading
import serial.tools.list_ports
import time


# -----------------------------
# Data acquisition
# -----------------------------
class MotionReceiver(threading.Thread):
    """
    Background thread that listens to the defined serial port and
    pushes motion values to a shared deque.
    """

    def __init__(self, port, baudrate, motion_buffer, use_mock_if_fail=True):
        super().__init__(daemon=True)
        self.port_name = port
        self.baudrate = baudrate
        self.motion_buffer = motion_buffer
        self.use_mock_if_fail = use_mock_if_fail
        self.running = False
        self.serial = None

    def open_port(self):
        # Try the configured port first
        try:
            self.serial = serial.Serial(self.port_name, self.baudrate, timeout=1)
            print(f"Connected to ZigBee at {self.port_name}")
            return True
        except Exception:
            # Auto-detect if default failed
            ports = list(serial.tools.list_ports.comports())
            # for p in ports:
            #     try:
            #         # Avoid obviously wrong ports if possible, or just try the first available
            #         self.serial = serial.Serial(p.device, self.baudrate, timeout=1)
            #         print(f"Auto-detected and connected to ZigBee at {p.device}")
            #         return True
            #     except Exception:
            #         continue

            self.serial = None
            return False

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
                    value = self.parse_motion_value(raw)
                    if value is not None:
                        self.motion_buffer.append(value)
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
