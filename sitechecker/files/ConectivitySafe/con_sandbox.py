import serial



def modemTTY():
    ports = []
    for port in range(10):
        try:
            modem_serial = serial.Serial(port= '/dev/ttyUSB{}'.format(port),
                                         baudrate=9600,
                                         timeout=5)
            atcommand = 'AT+CCINFO'
            command = atcommand + '\r'
            modem_serial.write(command.encode())
            modem_response = modem_serial.read(200)
            print("port {0} reponse is: {1}".format(port,modem_response))
            if "OK" in modem_response.decode("utf-8") :
                ports.append(port)
        except Exception as e:
            print(e)
            print("port {} doesnt answer".format(port))
    return ports

if __name__ == "__main__":
    print(modemTTY())