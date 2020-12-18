#!/usr/bin/python3
"""
Commande de cuve à vagues NOVA Physics

Gui pour commande d'un arduino

Fichier librarie pour commande l'arduino
"""
from serial import Serial
from serial.tools import list_ports
import os


class WaveGenArduino:
    """Class to handle arduino as a square signal generator"""
    pulse_freq_conversion_factor = 3200  # conversion factor from rotationnal freq to excitation freq
    __serial_connection = None

    def __init__(self, port=None, debug_func=None):
        """init"""
        self._debug_func = debug_func
        self._port = port
        # if port is not set, pick the first one with an arduino attached to it
        if (port == None):
            ports_list = self.list_arduino_ports()
            if ports_list != []:
                self._port = ports_list[0]
                self.__d("Serial: port set to {:s}".format(self._port))

    def __d(self, s):
        """more display in a standalone debug (no gui)"""
        if self._debug_func is not None:
            self._debug_func(s)

    def list_arduino_ports(self):
        """list serial ports where an arduino is connected"""
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
        """Connect to the Arduino"""
        self.__serial_connection = Serial(self._port, baudrate=115200)
        if self.__serial_connection.is_open:
            self.__d("Serial: Connected")
            return True
        return False

    def disconnect(self):
        """Disconnect from Arduino"""
        if self.__serial_connection is not None:
            self.__serial_connection.close()
            self.__serial_connection = None
            self.__d("Serial: disconnected")

    def _send_command(self, cmd):
        """Send command over serial connection"""
        bytes_cmd = bytes(cmd,'utf-8')
        self.__serial_connection.write(bytes_cmd)
        self.__d("Serial: Sent command {:s}".format(repr(bytes_cmd)))

    def _freq_to_motor_freq(self, freq):
        """Convert frequencies (and number of burst) in the real ones"""
        return int(freq * self.pulse_freq_conversion_factor)

    def continuous(self, freq):
        """start generator in a continous mode"""
        motor_pulse_freq = self._freq_to_motor_freq(freq)
        self._send_command("C{:d}\n".format(motor_pulse_freq))

    def burst(self, n, freq):
        """make the generator start only for n pulse at the right freq"""
        motor_pulse_freq = self._freq_to_motor_freq(freq)
        n = self._freq_to_motor_freq(n)
        self._send_command("B{:d},{:d}\n".format(n, motor_pulse_freq))

    def stop(self):
        """stops the generator"""
        self._send_command("S\n")

    def query_state(self):
        """ask arduino to tell its state: 0-> stop, 1-> continous, 2-> Burst"""
        self._send_command("?\n")


# Test code to run standalone
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

