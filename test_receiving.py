import serial
import time

# Open the Pi 1B+ UART
ser = serial.Serial("/dev/ttyAMA0", 9600, timeout=1)  # 9600 is safer for Pi 1B+

print("Coordinator running. Waiting for messages from Router...")
print("Press Ctrl+C to exit.\n")

try:
    while True:
        # Read a line from the Zigbee module
        line = ser.readline()
        if line:
            # Decode bytes to string
            msg = line.decode("utf-8").strip()
            print(f"Received from Router: {msg}")

        # Small delay to prevent CPU overuse
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Exiting...")
    ser.close()
