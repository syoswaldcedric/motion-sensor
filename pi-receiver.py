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
    print("Pi B running (Router/End Device)")
    time.sleep(2)  # give module time to initialize

    counter = 0
    try:
        while True:
            # Read incoming message
            incoming = read_message()
            if incoming:
                print(f"Received: {incoming}")

                # Optionally reply back
                reply = f"Hello from Pi B #{counter}"
                send_message(reply)
                # print(f"Sent: {reply}")
                counter += 1

            time.sleep(1)

    except KeyboardInterrupt:
        print("Exiting Pi B...")
        ser.close()
