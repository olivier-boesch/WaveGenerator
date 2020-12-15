/*
Square Waveform Generator asynchronous
 
 Olivier Boesch (c) 2020
 */

#define SERIAL_BAUDRATE 115200
//#define DEBUG
#define PORT_OUT PORTB
#define PIN_OUT 10 //8<->13 only
#define SERIAL_TIMEOUT 10 //ms
#define MAX_FREQ 14000 //Hz
#define TERMINATOR '\n'

class Pulse
{
public:
  Pulse(int pin);
  void start_continuous(unsigned long freq);
  void start_burst(unsigned long n, unsigned long freq);
  void stop();
  void update();
  byte get_mode();
private:
  byte _pin_mask;
  bool _state;
  byte _mode; //0: stop, 1: continuous, 2: pulse
  unsigned long _semi_period; //µs
  unsigned long _n_pulses; //number
  unsigned long _time_change; //µs
  void _toggle_output();
  bool _is_output_low();
};

Pulse::Pulse(int pin){
  this->_pin_mask = 1 << (pin-8);
  pinMode(pin, OUTPUT);
  this->stop();
}

byte Pulse::get_mode(){
  return this->_mode;
}

void Pulse::start_continuous(unsigned long freq){
  if((freq <= MAX_FREQ) && (freq > 0)){
    this->_mode = 1; 
    this->_semi_period = (unsigned long) (1000000.0 / (2*freq)); // half period
    this->_time_change = micros() + this->_semi_period;
#ifdef DEBUG
    Serial.print("Cont. f=");
    Serial.print(freq);
    Serial.print("Hz; T=");
    Serial.print(this->_semi_period);
    Serial.println(" micro sec");
#endif
  }
}

void Pulse::start_burst(unsigned long n, unsigned long freq){
  if((freq <= MAX_FREQ) && (freq > 0) && (n > 0)){
    this->_n_pulses = n;
    this->_mode = 2; 
    this->_semi_period = (unsigned long) (1000000.0 / (2*freq));
    this->_time_change = micros() + this->_semi_period;
#ifdef DEBUG
    Serial.print("Burst of ");
    Serial.print(n);
    Serial.print(" Pulses; f=");
    Serial.print(freq);
    Serial.print("Hz; T=");
    Serial.print(this->_semi_period);
    Serial.println(" micro sec");
#endif
  }
}

void Pulse::stop(){
  this->_time_change = 0;
  PORT_OUT = PORT_OUT & ~this->_pin_mask;
  this->_mode = 0;
#ifdef DEBUG
  Serial.println("Stop");
#endif
}

void Pulse::update(){
  if((this->_mode != 0) && (this->_time_change < micros())){
    this->_toggle_output();
    this->_time_change = micros() + this->_semi_period;
    if((this->_mode == 2)&& (this->_is_output_low())){
      this->_n_pulses -= 1;
      if(this->_n_pulses == 0)
        this->stop();
    }
  }  
}

void Pulse::_toggle_output(){
  PORT_OUT ^= this->_pin_mask;
}

bool Pulse::_is_output_low(){
  return (bool) !(PORT_OUT  & this->_pin_mask);
}

Pulse pulse_gen(PIN_OUT);

void update_config(){
  if(Serial.available()){
    String buffer;
    long n_pulses;
    long frequency;
    int comma;
    String sfreq;
    buffer = Serial.readStringUntil(TERMINATOR);
#ifdef DEBUG
    Serial.println(buffer);
#endif
    if(buffer.length() > 0){
      switch(buffer[0]){
      case 'S': //Stop
        pulse_gen.stop();
        break;
      case 'C': //Continuous
        frequency = buffer.substring(1).toInt();
        pulse_gen.start_continuous(frequency);
        break;
      case 'B': //Burst
        comma = buffer.indexOf(',');
        n_pulses = buffer.substring(1,comma).toInt();
        frequency = buffer.substring(comma+1).toInt();
        pulse_gen.start_burst(n_pulses, frequency);
        break;
      case '?': //Query current mode
        Serial.println(pulse_gen.get_mode());
      }
    }
  }
}

void setup(){
  Serial.begin(SERIAL_BAUDRATE); //start serial
  Serial.setTimeout(SERIAL_TIMEOUT);
#ifdef DEBUG
  while(!Serial);
  Serial.println("Starting...");
#endif
}

void loop(){
  update_config();
  pulse_gen.update();
}


