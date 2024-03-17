import serial
import time


def send_command(ser, module_id, command):
    ser.write(bytes([command, module_id]))
    response = ser.read_until(
        expected=bytes([0x01, 0x01, 0x03, 0x00, 0x01, 0x01, 0x1E, 0xFC])
    )
    print("Response:", response)


def main():
    ser = serial.Serial('/dev/ttys008', 57600, timeout=1)  # Adjust port as needed

    print("Serial client started")

    try:
        # Example commands
        send_command(ser, 0x01, 0x03)  # Start command to module 1
        time.sleep(1)  # Wait for response


    except KeyboardInterrupt:
        print("Serial client stopped")
    finally:
        ser.close()


if __name__ == "__main__":
    main()
