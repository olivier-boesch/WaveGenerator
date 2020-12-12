#!/usr/bin/python3
"""
"""
from kivy.app import App
from kivy.logger import Logger
from kivy.factory import Factory
from kivy.clock import Clock
import wavegen_arduino


class WaveGenApp(App):
    title = 'Waveform Generator'
    generator = wavegen_arduino.WaveGenArduino(None,Logger.info)
    repeat_event = None

    def on_start(self):
        if not self.generator.connect():
            d = Factory.MessagePopup()
            d.open()

    def on_stop(self):
        self.generator.disconnect()

    @staticmethod
    def format_text(val, dec):
        fstr = "{:." + str(dec) + "f}"
        return fstr.format(val)

    def reflect_val(self, who, textinput, slider, min_val, max_val, dec):
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
        if not is_burst:
            self.root.ids['pulse'].disabled = True
            self.root.ids['repeat_pulse'].disabled = True
        else:
            self.root.ids['pulse'].disabled = False
            self.root.ids['repeat_pulse'].disabled = False

    def set_generator(self, mode, freq, n):
        if mode == 'Burst':
            self.generator.burst(int(n), float(freq))
            if self.root.ids['checkbox_repeat_pulses'].active:
                every = int(self.root.ids['spinner_repeat_pulses'].text[:-1])
                self.repeat_event = Clock.schedule_interval(lambda dt: self.generator.burst(int(n), float(freq)), every)
        elif mode == 'Continuous':
            self.generator.continuous(float(freq))

    def stop_generator(self):
        self.generator.stop()
        if self.repeat_event is not None:
            self.repeat_event.cancel()
            self.repeat_event = None


app = WaveGenApp()
app.run()
