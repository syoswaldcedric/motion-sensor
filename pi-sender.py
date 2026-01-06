import serial
import time

# Serial setup
ser = serial.Serial("/dev/ttyAMA0", 9600, timeout=1)


def send_message(msg):
    ser.write(msg.encode("utf-8") + b"\n")


def read_message():
    line = ser.readline()
    if line:
        return line.decode("utf-8").strip()
    return None


if __name__ == "__main__":
    print("Pi A running (Coordinator)")
    time.sleep(2)  # give module time to initialize

    counter = 0
    try:
        while True:
            # Send a test message
            message = f"Hello from Pi A #{counter}"
            send_message(message)
            print(f"Sent: {message}")

            # Read incoming message (if any)
            incoming = read_message()
            if incoming:
                print(f"Received: {incoming}")

            counter += 1
            time.sleep(2)

    except KeyboardInterrupt:
        print("Exiting Pi A...")
        ser.close()
