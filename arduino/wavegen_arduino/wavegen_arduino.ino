/*
Square Waveform Generator asynchronous using tone

 Olivier Boesch (c) 2020-2021
*/

#define SERIAL_BAUDRATE 115200
//should we debug ? (uncomment the following line to do so)
//#define DEBUG
//don't wait serial forever
#define SERIAL_TIMEOUT 10 //ms
//don't output more than this frequency (5Hz wave -- 16000/3200)
#define MAX_FREQ 16000 //Hz
//don't output less than this frequency (~9.10^-3 Hz wave -- 31/3200 -- required by the tone function)
#define MIN_FREQ 31 //Hz
//each command ends with this
#define TERMINATOR '\n'
//pin
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
  unsigned long _time_end; //µs - time to stop the burst
};

Pulse::Pulse(int pin){
  //remember the pin
  this->_pin = pin;
  //begin stopped
  this->stop();
  this->_time_end = 0;
}

byte Pulse::get_mode(){
  //return current mode
  return this->_mode;
}

void Pulse::start_continuous(unsigned long freq){
  //change only if frequency is valid
  if((freq <= MAX_FREQ) && (freq >= MIN_FREQ)){
    //set current mode
    this->_mode = 1;
    //start output signal generation
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
    //set current mode
    this->_mode = 2;
    //compute when the burst should end
    this->_time_end = micros() + (unsigned long)((double)n/(double)freq*1000000.0); //when should we stop the burst ?
    //start output signal generation
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
  //set current mode to 0
  this->_mode = 0;
  //stop signal generation
  noTone(this->_pin);
#ifdef DEBUG
  Serial.println("Stop");
#endif
}

void Pulse::update(){
  //is it time to end the burst ?
  if((this->_mode == 2) && (micros() >= this->_time_end)){
    this->stop();
  }
}

Pulse * pulse_gen;

void setup(){
  pulse_gen = new Pulse(GENERATOR_PIN);
  Serial.begin(SERIAL_BAUDRATE); //start serial
  Serial.setTimeout(SERIAL_TIMEOUT);
#ifdef DEBUG //in debug case, we should wait for serial connection
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
    //read the complete command
    buffer = Serial.readStringUntil(TERMINATOR);
    #ifdef DEBUG
    Serial.println(buffer);
    #endif
    if(buffer.length() > 0){
      //the first character is the kind of command 
      switch(buffer[0]){
      case 'S': //Stop
        //stop the generator
        pulse_gen->stop();
        break;
      case 'C': //Continuous
        //following integer is the real output freq 
        frequency = buffer.substring(1).toInt();
        //start continuous generation
        pulse_gen->start_continuous(frequency);
        break;
      case 'B': //Burst
        //the comma seprates the number of pulses and the frequency
        comma = buffer.indexOf(',');
        //first integer is the number of pulses
        n_pulses = buffer.substring(1,comma).toInt();
        //second integer is the frequency
        frequency = buffer.substring(comma+1).toInt();
        // start emitting a burst
        pulse_gen->start_burst(n_pulses, frequency);
        break;
      case '?': //Query current mode
        //return current mode (as an integer): 0-> stop, 1-> continuous, 2->Burst (will go to 0 when the burst ends)
        Serial.println(pulse_gen->get_mode());
      }
    }
  }
  //update the generator (to end burst at the right time)
  pulse_gen->update();
}
