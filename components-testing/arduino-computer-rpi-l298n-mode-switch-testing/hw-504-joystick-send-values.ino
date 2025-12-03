
/*
STEP 1: Arduino sends the coordinates to computer

The order of running the code:

  1. Upload the hw-504-joystick-send-values.ino to Arduino.

  2. Run pi-receiver.py on the Raspberry Pi first, and it will start listening on the specified port and wait for a connection.

  3. Next, run computer-bridge.py on the computer. It will connect to the Raspberry Pi and start reading from the Arduino.
        Once the double-press on the joystick is done, the Pi will start receiving and printing the joystick data.
      
*/


// Arduino pin numbers
const int SW_pin = 8; // digital pin connected to switch output
const int X_pin = A0; // analog pin connected to X output
const int Y_pin = A1; // analog pin connected to Y output

// RGB LED pins
int redPin = 6;
int bluePin = 7;


// Double press variables
unsigned long lastPressTime = 0;
const unsigned long doublePressDelay = 500; // max time between presses in milliseconds
int pressCount = 0;
bool sendingEnabled = false;

void setup() {
  pinMode(SW_pin, INPUT_PULLUP); // internal pullup resistor
  Serial.begin(9600);

  pinMode(redPin, OUTPUT);
  pinMode(bluePin, OUTPUT);

  //start LED as OFF (remote is OFF)
  digitalWrite(redPin, HIGH);   // RED
  digitalWrite(bluePin, LOW);
}

void loop() {
  // Read joystick button: 1(HIGH) if not pressed, 0(LOW) if pressed
  int swState = digitalRead(SW_pin);
  
  static int lastSwState = HIGH;
  
  if (lastSwState == HIGH && swState == LOW) { // button pressed
    unsigned long currentTime = millis();
    if (currentTime - lastPressTime < doublePressDelay) {
      pressCount++;
    } else {
      pressCount = 1;
    }
    lastPressTime = currentTime;
    
    if (pressCount == 2) {
      sendingEnabled = !sendingEnabled; // toggle sending
      pressCount = 0;
      Serial.print("SENDING_");
      Serial.println(sendingEnabled ? "ON" : "OFF");

      // LED feedback for ON/OFF state
      if (sendingEnabled) {
        // ON = BLUE
        digitalWrite(redPin, LOW);
        digitalWrite(bluePin, HIGH);
      } else {
        // OFF = RED
        digitalWrite(redPin, HIGH);
        digitalWrite(bluePin, LOW);
      }

    }
  }
  lastSwState = swState;

  // Send joystick data only if sending is enabled
  if (sendingEnabled) {
    int x = analogRead(X_pin);
    int y = analogRead(Y_pin);
    int sw = swState == LOW ? 1 : 0; // active LOW: pressed=1, released=0
    Serial.print("X:");
    Serial.print(x);
    Serial.print("|Y:");
    Serial.print(y);
    Serial.print("|SW:");
    Serial.println(sw);
  }

  delay(50); // small delay for stability
}


/*

Reference:
Code adapted from https://lastminuteengineers.com/joystick-interfacing-arduino-processing/
Information learned from https://docs.cirkitdesigner.com/component/fa55a084-79fb-4baa-914f-2151a791a6b0/joystick-module
Code adapted from https://projecthub.arduino.cc/semsemharaz/interfacing-rgb-led-with-arduino-b59902

*/