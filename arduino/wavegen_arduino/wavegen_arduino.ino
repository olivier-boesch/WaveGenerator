/*
Square Waveform Generator asynchronous using tone

 Olivier Boesch (c) 2020
*/

#if defined(ARDUINO_SAMD_ZERO) && defined(SERIAL_PORT_USBVIRTUAL)
  // Required for Serial on Zero based boards
  #define Serial SERIAL_PORT_USBVIRTUAL
#endif

#define SERIAL_BAUDRATE 115200
//should we debug ?
//#define DEBUG
//don't wait serial forever
#define SERIAL_TIMEOUT 10 //ms
//don't output more than this frequency
#define MAX_FREQ 16000 //Hz
//don't output less than this frequency
#define MIN_FREQ 31 //Hz
//each command ends with this
#define TERMINATOR '\n'
//Pin
#define GENERATOR_PIN 10


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
  byte _pin; //where is the output pin ?
  bool _state; //current state true->HIGH
  byte _mode; //0: stop, 1: continuous, 2: pulse
  unsigned long _time_end; //µs - time to stop burst
};

Pulse::Pulse(int pin){
  this->_pin = pin;
  pinMode(pin, OUTPUT);
  this->stop();
  this->_time_end = 0;
}

byte Pulse::get_mode(){
  return this->_mode;
}

void Pulse::start_continuous(unsigned long freq){
  //change only if frequency is valid
  if((freq <= MAX_FREQ) && (freq >= MIN_FREQ)){
    this->_mode = 1;
    tone(this->_pin, freq);
#ifdef DEBUG
    Serial.print("Continuous f=");
    Serial.print(freq);
    Serial.println("Hz");
#endif
  }
}

void Pulse::start_burst(unsigned long n, unsigned long freq){
  //change only if frequency is valid
  if((freq <= MAX_FREQ) && (freq >= MIN_FREQ) && (n > 0)){
    this->_mode = 2;
    this->_time_end = micros() + (unsigned long)((double)n/(double)freq*1000000.0); //when should we stop the burst ?
    tone(this->_pin, freq);
#ifdef DEBUG
    Serial.print("Burst of ");
    Serial.print(n);
    Serial.print(" Pulses; f=");
    Serial.print(freq);
    Serial.println("Hz");
#endif
  }
}

void Pulse::stop(){
  this->_time_end = 0;
  this->_mode = 0;
  noTone(this->_pin);
#ifdef DEBUG
  Serial.println("Stop");
#endif
}

void Pulse::update(){
  //is it time to end the burst ?
  if((this->_mode == 2) && (this->_time_end <= micros())){
    this->stop();
  }
}

Pulse * pulse_gen;

void setup(){
  pulse_gen = new Pulse(GENERATOR_PIN);
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
