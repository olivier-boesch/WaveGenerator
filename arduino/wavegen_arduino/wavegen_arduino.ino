/*
Square Waveform Generator asynchronous

 Olivier Boesch (c) 2020
*/

#define SERIAL_BAUDRATE 115200
//should we debug ?
//#define DEBUG
//port to ouput on by direct manipulation
#define PORT_OUT PORTB //PORTB for pins 8 to 13, PORTD for pins 0 to 7
#define PIN_FIRST 8 //8 for PORTB and 0 for PORTD
// output pin
#define PIN_OUT 10 //8<->13 only on port B
//don't wait serial forever
#define SERIAL_TIMEOUT 10 //ms
//don't output more than this frequency
#define MAX_FREQ 16000 //Hz
//each command ends with this
#define TERMINATOR '\n'


//class for asynchronous square signal generation
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
  byte _pin_mask; //where is the output pin ?
  bool _state; //current state true->HIGH
  byte _mode; //0: stop, 1: continuous, 2: pulse
  unsigned long _semi_period; //µs - half period of signal
  long _n_pulses; //number
  unsigned long _time_change; //µs - next time to change
  void _toggle_output();
  bool _is_output_low();
};

Pulse::Pulse(int pin){
  this->_pin_mask = 1 << (pin-PIN_FIRST);
  pinMode(pin, OUTPUT);
  this->stop();
}

byte Pulse::get_mode(){
  return this->_mode;
}

void Pulse::start_continuous(unsigned long freq){
  //change only if frequency is valid
  if((freq <= MAX_FREQ) && (freq > 0)){
    this->_mode = 1;
    this->_semi_period = (unsigned long) (1000000.0 / (2*freq)); // half period in µs
    this->_time_change = micros() + this->_semi_period; //when the next change should occur ?
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
  //change only if frequency is valid
  if((freq <= MAX_FREQ) && (freq > 0) && (n > 0)){
    this->_n_pulses = n;
    this->_mode = 2;
    this->_semi_period = (unsigned long) (1000000.0 / (2*freq)); //half period
    this->_time_change = micros() + this->_semi_period; //when the next change should occur ?
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
  this->_time_change = 0; //don't change anymore on next update
  PORT_OUT = PORT_OUT & ~this->_pin_mask; //put on low state
  this->_mode = 0;
#ifdef DEBUG
  Serial.println("Stop");
#endif
}

void Pulse::update(){
  //is it time to change the output state ?
  if((this->_time_change <= micros()) && (this->_mode != 0)){
    this->_toggle_output();
    //set the next time to change
    this->_time_change = micros() + this->_semi_period;
    //are we in burst mode ?
    if((this->_is_output_low()) && (this->_mode == 2)){
      #ifdef DEBUG
      Serial.print("pulses: ");
      Serial.println(this->_n_pulses);
      #endif
      //one pulse has been done
      this->_n_pulses --;
      //if no more pulse -> stop
      if(this->_n_pulses < 0)
        this->stop();
    }
  }
}

void Pulse::_toggle_output(){
  //reverse output
  PORT_OUT ^= this->_pin_mask;
}

bool Pulse::_is_output_low(){
  //are we in a low state ?
  return (bool) !(PORT_OUT  & this->_pin_mask);
}

Pulse * pulse_gen;

void setup(){
  pulse_gen = new Pulse(PIN_OUT);
  Serial.begin(SERIAL_BAUDRATE); //start serial
  Serial.setTimeout(SERIAL_TIMEOUT);
#ifdef DEBUG
  while(!Serial);
  Serial.println("Starting...");
#endif
}

void loop(){
  //is there a command ready to be received?
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
        pulse_gen->stop();
        break;
      case 'C': //Continuous
        frequency = buffer.substring(1).toInt();
        pulse_gen->start_continuous(frequency);
        break;
      case 'B': //Burst
        comma = buffer.indexOf(',');
        n_pulses = buffer.substring(1,comma).toInt();
        frequency = buffer.substring(comma+1).toInt();
        pulse_gen->start_burst(n_pulses, frequency);
        break;
      case '?': //Query current mode
        Serial.println(pulse_gen->get_mode());
      }
    }
  }
  pulse_gen->update();
}


