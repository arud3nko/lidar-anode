"""
https://jamesthom.as/2021/01/virtual-serial-ports-using-socat/


"""


import serial
import time


def generate_response(command, module):
    time.sleep(1)
    if command == 0x01:  # Stop
        response = bytes([0x01, module, 0x03, 0x00, 0x01, 0x00, 0xDE, 0x3D])
    elif command == 0x02 or command == 0x03:  # Initial or Start
        response = bytes([0x01, module, 0x03, 0x00, 0x01, 0x01, 0x1E, 0xFC])
    elif command == 0x88:  # Request state
        response = bytes([0x01, module, 0x01, 0x00, 0x01, 0b00000000])  # Sample response, adjust as needed
    else:
        response = b''  # Unknown command, no response
    return response


def main():
    ser = serial.Serial('/dev/ttys007', 57600, timeout=1)  # Adjust port as needed

    print("Serial server started")

    try:
        while True:
            command = ser.read(1)  # Read command byte
            if command:
                module = ser.read(1)  # Read module byte
                response = generate_response(int.from_bytes(command, "big"), int.from_bytes(module, "big"))
                ser.write(response)  # Send response
                print("Response sent:", response)
    except KeyboardInterrupt:
        print("Serial server stopped")
    finally:
        ser.close()


if __name__ == "__main__":
    main()
