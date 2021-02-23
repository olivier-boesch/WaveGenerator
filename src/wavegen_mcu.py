#!/usr/bin/python3
"""
Commande de cuve à vagues NOVA Physics

Gui pour commande d'un arduino

Fichier librarie pour commande l'arduino
"""

from kivy.utils import platform
if platform in ['win', 'linux']:
    from serial import Serial
    from serial.tools import list_ports
elif platform == 'android':
    from usb4a import usb
    from usbserial4a import serial4a

from kivy.logger import Logger


def list_arduino_ports():
    """list serial ports where an arduino is connected"""
    arduino_list = []
    if platform == 'android':
        usb_device_list = usb.get_usb_device_list()
        for device in usb_device_list:
            if device.getVendorId() == 9025:  # 9025 is the vid of 'Arduino LLC'
                arduino_list.append(device.getDeviceName())
                self.android_device = device
    if platform in ['win','linux']:
        l = list_ports.comports()
        for item in l:
            if item.vid == 9025:  # 9025 is the vid of 'Arduino LLC'
                arduino_list.append(item.device)
    Logger.debug("Serial: Arduino found {}".format(str(arduino_list)))
    return 115200, '\n', arduino_list  # return baudrate and list


class WaveGenSerial:
    """Class to handle arduino as a square signal generator"""
    pulse_freq_conversion_factor = 3200  # conversion factor from rotational freq to excitation freq
    __serial_connection = None

    def __init__(self, port=None, debug_func=None):
        """init"""
        self._debug_func = debug_func
        self._port = port
        # if port is not set, pick the first one with an arduino attached to it
        if (port == None):
            baudrate, endline, ports_list = list_arduino_ports()
            if ports_list != []:
                self._port = ports_list[0]
                self._baudrate = baudrate
                self._endline = endline
                self.__d("Serial: port set to {:s}".format(self._port))

    def __d(self, s):
        """more display in a standalone debug (no gui)"""
        if self._debug_func is not None:
            self._debug_func(s)

    def connect(self):
        """Connect to the Arduino"""
        if self._port is None:
            return False
        if platform == 'android':
            if not usb.has_usb_permission(self.android_device):
                usb.request_usb_permission(self.android_device)
                return None
            self.__serial_connection = serial4a.get_serial_port( self._port, self._baudrate, 8, 'N', 1)
            if self.__serial_connection and self.__serial_connection.is_open:
                self.__d("Serial: Connected")
                return True
        else:
            self.__serial_connection = Serial(self._port, baudrate=self._baudrate)
            if self.__serial_connection.is_open:
                self.__d("Serial: Connected")
                return True
        self.__serial_connection = None
        self._port = None
        return False

    def disconnect(self):
        """Disconnect from Arduino"""
        if self.__serial_connection is not None:
            self.__serial_connection.close()
            self.__serial_connection = None
            self.__d("Serial: disconnected")

    def _send_command(self, cmd):
        """Send command over serial connection"""
        bytes_cmd = bytes(cmd+self._endline, 'utf-8')
        if self.__serial_connection is not None:
            self.__serial_connection.write(bytes_cmd)
            self.__d("Serial: Sent command {:s}".format(repr(bytes_cmd)))

    def _freq_to_motor_freq(self, freq):
        """Convert frequencies (and number of burst) in the real ones"""
        return int(freq * self.pulse_freq_conversion_factor)

    def continuous(self, freq):
        """start generator in a continous mode"""
        motor_pulse_freq = self._freq_to_motor_freq(freq)
        self._send_command("C{:d}".format(motor_pulse_freq))

    def burst(self, n, freq):
        """make the generator start only for n pulse at the right freq"""
        motor_pulse_freq = self._freq_to_motor_freq(freq)
        n = self._freq_to_motor_freq(n)
        self._send_command("B{:d},{:d}".format(n, motor_pulse_freq))

    def stop(self):
        """stops the generator"""
        self._send_command("S")

    def query_state(self):
        """ask arduino to tell its state: 0-> stop, 1-> continous, 2-> Burst"""
        self._send_command("?")


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
