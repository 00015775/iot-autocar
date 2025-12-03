// testing joystick from computer connected to Arduino Uno R3 via USB
// upload this code to Arduino for testing

const int SW_pin = 8; // digital pin, receives 0 if button is pressed, 1 otherwise
const int X_pin = A0; // control X-axis of joystick
const int Y_pin = A1; // control Y-axis of joystick

void setup() {
  pinMode(SW_pin, INPUT_PULLUP);
  Serial.begin(9600);
}

void loop() {
  int sw = digitalRead(SW_pin); 
  int x = analogRead(X_pin);
  int y = analogRead(Y_pin);

  // Sends CSV coordinates to computer -> RPi
  Serial.print(sw);
  Serial.print(",");
  Serial.print(x);
  Serial.print(",");
  Serial.println(y);

  delay(50);
}

/*

Reference:
Code adapted from https://lastminuteengineers.com/joystick-interfacing-arduino-processing/
Information learned from https://docs.cirkitdesigner.com/component/fa55a084-79fb-4baa-914f-2151a791a6b0/joystick-module

*/