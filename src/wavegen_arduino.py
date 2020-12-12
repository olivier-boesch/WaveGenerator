from serial import Serial, EIGHTBITS, PARITY_NONE, STOPBITS_ONE
from serial.tools import list_ports
import os


class WaveGenArduino:
    pulse_freq_conversion_factor = 3200
    __serial_connection = None

    def __init__(self, port=None, debug_func=None):
        self._debug_func = debug_func
        self._port = port
        if (port == None):
            ports_list = self.list_arduino_ports()
            if ports_list != []:
                self._port = ports_list[0]
                self.__d("Serial: port set to {:s}".format(self._port))

    def __d(self, s):
        if self._debug_func is not None:
            self._debug_func(s)

    def list_arduino_ports(self):
        if os.name == 'posix':
            prefix = '/dev/'
        else:
            prefix = ''
        arduino_list = []
        l = list_ports.comports()
        for item in l:
            if item.vid == 9025:  # 9025 is the vid of 'Arduino LLC'
                arduino_list.append(prefix+item.name)
        self.__d("Serial: available ports "+str(arduino_list))
        return arduino_list

    def connect(self):
        self.__serial_connection = Serial(self._port)
        if self.__serial_connection.is_open:
            self.__d("Serial: Connected")
            return True
        return False

    def disconnect(self):
        self.__serial_connection.close()
        self.__serial_connection = None
        self.__d("Serial: disconnected")

    def _send_command(self, cmd):
        bytes_cmd = bytes(cmd,'utf-8')
        self.__serial_connection.write(bytes_cmd)
        self.__d("Serial: Sent command {:s}".format(repr(bytes_cmd)))

    def _freq_to_motor_freq(self, freq):
        return int(freq * self.pulse_freq_conversion_factor)

    def continuous(self, freq):
        motor_pulse_freq = self._freq_to_motor_freq(freq)
        self._send_command("C{:d}\n".format(motor_pulse_freq))

    def burst(self, n, freq):
        motor_pulse_freq = self._freq_to_motor_freq(freq)
        n = self._freq_to_motor_freq(n)
        self._send_command("B{:d},{:d}\n".format(n, motor_pulse_freq))

    def stop(self):
        self._send_command("S\n")

    def query_state(self):
        self._send_command("?\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("command", type=str)
    args = parser.parse_args()
    cmd = args.command
    w = WaveGenArduino()
    if not w.connect():
        exit(1)
    cmd_type = cmd[0]
    if cmd_type == 'S':
        w.stop()
    elif cmd_type == 'C':
        freq = float(cmd[1:])
        w.continuous(freq)
    elif cmd_type == 'B':
        cmd_args = cmd[1:].split(',')
        n = int(cmd_args[0])
        freq = float(cmd_args[1])
        w.burst(n, freq)

