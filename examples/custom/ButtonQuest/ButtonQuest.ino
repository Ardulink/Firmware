/*
Copyright 2013 project Ardulink http://www.ardulink.org/

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

This sketch is an example to understand how Arduino can recognize ALProtocol. 
However, it can easily be reused for their own purposes or as a base for a library. 
Read carefully the comments. When you find "this is general code you can reuse"
then it means that it is generic code that you can use to manage the ALProtocol. 
When you find "this is needed just as example for this sketch" then it means that 
you code useful for a specific purpose. In this case you have to modify it to suit 
your needs.
*/

#include <Tiny4kOLED.h>
#include <stdio.h>

#define BUFFER_SIZE 64
#define BUTTON_COUNT 4
#define BUTTON_PIN_1 3
#define BUTTON_PIN_2 8
#define BUTTON_PIN_3 7
#define BUTTON_PIN_4 2

boolean toBePressed[BUTTON_COUNT];
boolean initialized;

bool handleCustomMessage(String customId, String value, char* rplyBuffer) {
  if (!initialized) {
    pinMode(BUTTON_PIN_1, INPUT);
    pinMode(BUTTON_PIN_2, INPUT);
    pinMode(BUTTON_PIN_3, INPUT);
    pinMode(BUTTON_PIN_4, INPUT);

    // oled.begin();
    // oled.clear();
    // oled.on();
    initialized = true;
  }
  
  if (customId == "setbutton") {
    if (value.startsWith("on/")) {
      setToBePressed(value.substring(3).toInt(), true);
      return true;
    } else if (value.startsWith("off/")) {
      setToBePressed(value.substring(4).toInt(), false);
      return true;
    }
  } else if (customId == "getResult") {
    rplyAppend("result=");
    rplyAppend(getResult().c_str());
    return true;
  }
  return false;
}

void setToBePressed(int index, boolean b) {
  toBePressed[index - 1] = b;

  static char buffer[BUFFER_SIZE];
  buffer[0] = '\0';
  int pos = 0;
  for (int i = 0; i < BUTTON_COUNT; i++) {
    if (toBePressed[i]) {
      sprintf(&buffer[pos++], "%d", (i + 1));
      buffer[pos++] = ' ';
    }
  }
  buffer[pos] = '\0';

  // oled.clear();
  // oled.setCursor(0, 0);
  // oled.print(buffer);
}

String getResult() {
  String result = "";
  boolean pressed[BUTTON_COUNT];
  int buttonPins[BUTTON_COUNT] = {BUTTON_PIN_1, BUTTON_PIN_2, BUTTON_PIN_3, BUTTON_PIN_4};

  for (int i = 0; i < BUTTON_COUNT; i++) {
    pressed[i] = digitalRead(buttonPins[i]) == HIGH;
    result += "Button " + String(i + 1) + " " + (pressed[i] ? "on" : "off") + " ";
  }

  boolean correct = true;
  for (int i = 0; i < BUTTON_COUNT; i++) {
    if (pressed[i] != toBePressed[i]) {
      correct = false;
      break; // No need to check further if already wrong
    }
  }

  return result + " " + (correct ? "RIGHT" : "WRONG") + "!";
}

bool handleKprs(const char* cParams, size_t length) {
  // here you can write your own code. For instance the commented code change pin intensity if you press 'a' or 's'
  // take the command and change intensity on pin 11 this is needed just as example for this sketch
  
  bool commandHandledSuccessfully = false;
  return commandHandledSuccessfully;
}
