# Protocol

## Burst

Command :

B5,1500\n : Burst of 5 pulses at 1500 Hz

## Continuous

Command :

C2000\n : Continuous at 2000Hz

## stop

S\n : stops the motor

## Query state

?\n : returns the current mode

0: stop
1: continuous
2: burst (when not finished, 0 otherwise)