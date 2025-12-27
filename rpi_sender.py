import sys
import time
import serial

# import RPi.GPIO; if its not available (e.g. on Windows/Mac dev machine), use mock
try:
    import RPi.GPIO as GPIO

    IS_RPI = True
except ImportError:
    IS_RPI = False
    print("RPi.GPIO not found. Running in MOCK mode (simulated sensor).")

# -----------------------------
# Configuration
# -----------------------------
PIR_PIN = 4  # GPIO pin connected to PIR output (BCM numbering)
SERIAL_PORT = "/dev/ttyUSB0"  # Adjust if using ttyAMA0 or other
BAUD_RATE = 9600
CHECK_INTERVAL = 0.5  # How often to check sensor state (seconds)


def setup_gpio():
    if not IS_RPI:
        return
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIR_PIN, GPIO.IN)


def read_pir():
    if not IS_RPI:
        # Mock behavior: random motion every few seconds
        import random

        return 1 if random.random() > 0.8 else 0

    # Read actual pin
    return GPIO.input(PIR_PIN)


def main():
    setup_gpio()

    # Initialize Serial
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Opened serial port {SERIAL_PORT} at {BAUD_RATE} baud.")
    except Exception as e:
        print(f"Error opening serial port {SERIAL_PORT}: {e}")
        # In mock mode, we might just want to print to stdout instead of crashing
        if IS_RPI:
            sys.exit(1)
        else:
            ser = None

    print("Components initialized. Starting loop...")
    print("Press Ctrl+C to exit.")

    last_state = -1

    try:
        while True:
            current_state = read_pir()

            # Send update only on state change or periodically if desired.
            # Here we send on change to keep traffic low, but heartbeats are also good.
            if current_state != last_state:
                msg = f"MOTION:{current_state}\n"

                if ser and ser.is_open:
                    ser.write(msg.encode("utf-8"))
                    ser.flush()

                print(f"Sent: {msg.strip()}")
                last_state = current_state

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        if IS_RPI:
            GPIO.cleanup()
        if ser and ser.is_open:
            ser.close()


if __name__ == "__main__":
    main()
