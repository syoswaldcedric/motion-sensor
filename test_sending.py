import serial
import time

ser = serial.Serial("/dev/ttyAMA0", 9600, timeout=1)
num = 1
while True:
    msg = f"Hello from Router #{num}\n".encode("utf-8")
    ser.write(msg)
    print(f"Sent: {msg}")
    num += 1
    time.sleep(2)
