from time import sleep

def export_pins(pins):
    try:
        f = open("/sys/class/gpio/export", "w")
        f.write(str(pins))
        f.close()
        return "OK"
    except IOError:
        print("GPIO" + str(pins) + "already Exists, so skipping export gpio")
        return ("GPIO" + str(pins) + "already Exists, so skipping export gpio")

def setpindirection(pin_no, pin_direction):
    gpiopin = "gpio" + str(pin_no)
    pin = open("/sys/class/gpio/" + gpiopin + "/direction", "w")
    pin.write(pin_direction)
    pin.close()

def writepins(pin_no, pin_value):
    gpiopin = "gpio" + str(pin_no)
    pin = open("/sys/class/gpio/" + gpiopin + "/value", "w")
    if pin_value == 1:
      pin.write("1")
    else:
      pin.write("0")
    pin.close()

def bucle():
    export_pins(23)
    setpindirection(23, "out")
    while True:
        writepins(23, 0)
        sleep(45)
        writepins(23, 1)
        sleep(45)

def flanco():
    try:
        export_pins(23)
        setpindirection(23, "out")
        writepins(23, 0)
        sleep(1)
        writepins(23, 1)
        return True
    except:
        return False

if __name__ == "__main__":
    bucle()