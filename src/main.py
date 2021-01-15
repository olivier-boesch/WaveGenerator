#!/usr/bin/python3
"""

Commande de cuve à vagues NOVA Physics

Gui pour commande d'un arduino


"""

__version__ = '1.0.2'

# no console on output for windows
from kivy.utils import platform
if platform == 'win':
    import os
    os.environ['KIVY_NO_CONSOLELOG'] = '0'

from kivy.app import App
from kivy.logger import Logger
from kivy.factory import Factory
from kivy.clock import Clock
import wavegen_arduino


class WaveGenApp(App):
    """Main app class"""
    title = 'Waveform Generator'
    generator = wavegen_arduino.WaveGenArduino(None,Logger.info)
    repeat_event = None
    generator_started = False

    def on_start(self):
        """what to do just before start ?"""
        self.connect()

    def on_stop(self):
        """what to do just before stop ?"""
        if self.generator_started:
            self.generator.stop()
        self.generator.disconnect()

    def connect(self):
        ret = self.generator.connect()
        if ret is None:
            Clock.schedule_once(lambda dt: self.connect(), 0.5)
        elif ret == False:
            d = Factory.MessagePopup()
            d.open()

    def set_repeat(self, active):
            self.root.ids['every_repeat'].disabled = not active
            self.root.ids['spinner_repeat_pulses'].disabled = not active

    @staticmethod
    def format_text(val, dec):
        """how to format displyed text in textinput"""
        fstr = "{:." + str(dec) + "f}"
        return fstr.format(val)

    def reflect_val(self, who, textinput, slider, min_val, max_val, dec):
        """Reflect and constrain value between a textinput and a slider"""
        if textinput.text == self.format_text(slider.value, dec):
            return
        if (who == 'input') and (textinput.text != ''):
            if float(textinput.text) > max_val:
                val = max_val
                textinput.text = self.format_text(max_val, dec)
            elif float(textinput.text) < min_val:
                val = min_val
                textinput.text = self.format_text(min_val, dec)
            else:
                val = max(min_val, float(textinput.text))
            slider.value = val
        else:
            textinput.text = self.format_text(slider.value, dec)

    def set_mode(self, is_burst=False):
        """set ui possibilities regarding current mode"""
        if not is_burst:  # continuous mode
            self.root.ids['pulse'].disabled = True
            self.root.ids['repeat_pulse'].disabled = True
        else:  # Burst mode
            self.root.ids['pulse'].disabled = False
            self.root.ids['repeat_pulse'].disabled = False
            self.set_repeat(self.root.ids['checkbox_repeat_pulses'].active)

    def update_freq(self):
        """update freq live when running in continuous mode"""
        if self.generator_started:
            Logger.info("Freq: updating frequency live")
            freq = "{:.3f}".format(self.root.ids['slider_freq'].value)
            mode = self.root.ids['spinner_mode'].text
            if mode == 'Continuous':
                self.set_generator(mode, freq, 0)

    def set_generator(self, mode, freq, n):
        """start generator with right mode and characteristics"""
        if self.generator_started:
            self.stop_generator()
        if mode == 'Burst':
            Logger.info("Op: Start Generator (Burst of {:s} pulses at {:s} Hz".format(n, freq))
            self.generator.burst(int(n), float(freq))
            if self.root.ids['checkbox_repeat_pulses'].active:
                every = int(self.root.ids['spinner_repeat_pulses'].text[:-1])
                Logger.info("Op: Sheduling repeat bursts every {:d} s".format(every))
                if self.repeat_event is not None:
                    self.repeat_event.cancel()
                    self.repeat_event = None
                self.repeat_event = Clock.schedule_interval(lambda dt: self.generator.burst(int(n), float(freq)), every)
            self.generator_started = True
        elif mode == 'Continuous':
            Logger.info("Op: Start Generator (continuous at {:s} Hz".format(freq))
            self.generator.continuous(float(freq))
            self.generator_started = True

    def stop_generator(self):
        """stop generator"""
        Logger.info("Op: Stop Generator")
        self.generator_started = False
        self.generator.stop()
        if self.repeat_event is not None:
            self.repeat_event.cancel()
            self.repeat_event = None

if __name__ == "__main__":
    # create and start app
    app = WaveGenApp()
    app.run()
