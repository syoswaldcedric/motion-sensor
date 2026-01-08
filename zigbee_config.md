# steps to configure zigbee module as cordinator and router

## step 1: update pip

```bash
    sudo apt-get update
```

## step 2: install picocom

```bash
    sudo apt-get install picocom
```

## step 3: connect to zigbee module

```bash
    sudo picocom -b 9600 /dev/ttyAMA0
```

## step 4: configure zigbee module

```bash
    +++
```

## step 5: configure zigbee module as coordinator

```bash
    ATRE
    ATCE 0
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
