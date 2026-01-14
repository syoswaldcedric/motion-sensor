# steps to configure zigbee module as cordinator and router

# Enable UART on the raspberypi

```bash
    sudo raspi-config
       interface -> serial port -> Login over serial== No
    sudo reboot
```

## step 1: update pip

```bash
    sudo apt-get update
```

## step 2: install picocom

```bash
    sudo apt-get install -y picocom
```

## step 3: connect to zigbee module

```bash
    sudo picocom -b 9600 --echo /dev/ttyAMA0
    sudo picocom -b 9600 --echo /dev/serial0
```

## step 4: configure zigbee module

```bash
    +++
    <!-- wait for ok -->

```

## step 5: configure zigbee module as coordinator

```bash
    ATRE
    ATCE 0 (A == receiver/ cordinator)
    ATWR
    ATFR
```

## step 6: configure zigbee module as router

```bash
    ATRE
    ATCE 0
    ATWR
    ATFR
```
