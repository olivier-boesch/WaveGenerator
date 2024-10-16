#!/bin/env python3
"""

Commande de cuve à vagues NOVA Physics

Gui pour commande d'un arduino

"""
# no console on output for windows
import os
if os.name == 'nt':
    os.environ['KIVY_NO_CONSOLELOG'] = '1'

from kivy.config import Config
Config.set("graphics", "window_state", "maximized")

from kivy.app import App
from kivy.logger import Logger, LOG_LEVELS
Logger.setLevel((LOG_LEVELS['debug']))
from kivy.factory import Factory
from kivy.clock import Clock
import wavegen_mcu


class WaveGenApp(App):
    """Main app class"""
    title = 'Waveform Generator'
    icon = 'icon.png'
    generator = wavegen_mcu.WaveGenSerial(None, Logger.info)
    repeat_event = None
    generator_started = False
    harmonic = 0
    resonant_freq = 0.5

    def on_start(self):
        """what to do just before start ?"""
        self.connect()

    def on_stop(self):
        """what to do just before stop ?"""
        if self.generator_started:
            self.generator.stop()
        self.generator.disconnect()
        
    def on_pause(self):
        """what todo when the app is paused -> leave"""
        return False

    def connect(self):
        """ask the generator to connect to the arduino"""
        ret = self.generator.connect()
        if ret is None:
            Clock.schedule_once(lambda dt: self.connect(), 1)
        elif ret == False:
            d = Factory.NoBoxPopup()
            d.open()

    def disconnection_occurs(self):
        p = Factory.DisconnectBoxPopup()
        p.open()

    def set_repeat(self, active):
            self.root.ids['every_repeat'].disabled = not active
            self.root.ids['spinner_repeat_pulses'].disabled = not active

    @staticmethod
    def format_text(val, dec):
        """how to format displayed text in textinput"""
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
                if self.set_generator(mode, freq, 0) is not None:
                    self.disconnection_occurs()

    def set_generator(self, mode, freq, n):
        """start generator with right mode and characteristics"""
        if self.generator_started:
            self.stop_generator()
        if mode == 'Burst':
            Logger.info("Op: Start Generator (Burst of {:s} pulses at {:s} Hz".format(n, freq))
            if self.generator.burst(int(n), float(freq)) is not None:
                self.disconnection_occurs()
            if self.root.ids['checkbox_repeat_pulses'].active:
                every = int(self.root.ids['spinner_repeat_pulses'].text[:-1])
                Logger.info("Op: Sheduling repeat bursts every {:d} s".format(every))
                if self.repeat_event is not None:
                    self.repeat_event.cancel()
                    self.repeat_event = None
                self.repeat_event = Clock.schedule_interval(lambda dt: self.launch_burst(int(n), float(freq)), every)
            self.generator_started = True
        elif mode == 'Continuous':
            Logger.info("Op: Start Generator (continuous at {:s} Hz".format(freq))
            if self.generator.continuous(float(freq)) is not None:
                self.disconnection_occurs()
            self.generator_started = True

    def launch_burst(self, n, freq):
        if self.generator.burst(int(n), float(freq)) is not None:
            self.disconnection_occurs()

    def stop_generator(self):
        """stop generator"""
        Logger.info("Op: Stop Generator")
        self.generator_started = False
        if self.generator.stop() is not None:
            self.disconnection_occurs()
        if self.repeat_event is not None:
            self.repeat_event.cancel()
            self.repeat_event = None


# create and start app
app = WaveGenApp()
app.run()
