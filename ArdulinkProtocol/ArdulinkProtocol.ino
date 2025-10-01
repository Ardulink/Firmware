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


constexpr int DIGITAL_PIN_LISTENING_NUM = 14; // Change 14 if you have a different number of pins.
constexpr int ANALOG_PIN_LISTENING_NUM = 6;   // Change  6 if you have a different number of pins.

constexpr int TOTAL_PINS = DIGITAL_PIN_LISTENING_NUM + ANALOG_PIN_LISTENING_NUM;

#define MESSAGE_SEPARATOR '\n'
#define MESSAGE_SEPARATOR_RX MESSAGE_SEPARATOR
#define MESSAGE_SEPARATOR_TX MESSAGE_SEPARATOR

#define INVALID_LISTENED_VALUE (-2)

const size_t INPUT_BUFFER_SIZE = 128;
char inputBuffer[INPUT_BUFFER_SIZE];  // a inputBuffer to hold incoming data
size_t inputLength = 0;
bool stringComplete = false;          // whether the string is complete

constexpr size_t RPLY_BUFFER_SIZE = 128;
char rplyBuffer[RPLY_BUFFER_SIZE];
size_t rplyLength = 0;

boolean pinListening[TOTAL_PINS] = { false }; // Array used to know which pins on the Arduino must be listening.
int pinListenedValue[TOTAL_PINS] = { INVALID_LISTENED_VALUE }; // Array used to know which value is read last time.

#define UNLIMITED_LENGTH ((size_t)-1)

struct CommandHandler {
    const char* command;
    bool (*handler)(const char* params, size_t length);
};


bool parseIntPair(const char* cParams, int& first, int& second, char separator = '/') {
  const char* separatorPos = strchr(cParams, separator);
  if (!separatorPos) return false;
  first = atoi(cParams);
  second = atoi(separatorPos + 1);
  return true;
}

bool setAnalogListeningState(int pin, bool listening) {
  return setListeningState(pin, listening, DIGITAL_PIN_LISTENING_NUM + pin);
}

bool setDigitalListeningState(int pin, bool listening) {
  return setListeningState(pin, listening, pin);
}

bool setListeningState(int pin, bool listening, int arrayIndex) {
  pinListening[arrayIndex] = listening;
  pinListenedValue[arrayIndex] = INVALID_LISTENED_VALUE; // Reset the listened value to INVALID_LISTENED_VALUE.
  pinMode(pin, listening ? INPUT : OUTPUT);
  return true;
}

bool noop(const char* cParams, size_t length) {
  return true;
}

bool handlePpin(const char* cParams, size_t length) {
  int pin, value;
  if (!parseIntPair(cParams, pin, value)) return false;
  pinMode(pin, OUTPUT);
  analogWrite(pin, value);
  return true;
}

bool handlePpsw(const char* cParams, size_t length) {
  int pin, value;
  if (!parseIntPair(cParams, pin, value)) return false;
  pinMode(pin, OUTPUT);
  digitalWrite(pin, value == 1 ? HIGH : LOW);
  return true;
}

bool handleTone(const char* cParams, size_t length) {
  const char* separator1 = strchr(cParams, '/');
  if (!separator1) return false;
  const char* separator2 = strchr(separator1 + 1, '/');
  if (!separator2) return false;

  int pin = atoi(cParams);
  int frequency = atoi(separator1 + 1);
  int duration = atoi(separator2 + 1);

  if (duration == -1) {
    tone(pin, frequency);
  } else {
    tone(pin, frequency, duration);
  }
  return true;
}

bool handleNotn(const char* cParams, size_t length) {
  int pin = atoi(cParams);
  noTone(pin);
  return true;
}

bool handleSrld(const char* cParams, size_t length) {
  int pin = atoi(cParams);
  return setDigitalListeningState(pin, true);
}

bool handleSpld(const char* cParams, size_t length) {
  int pin = atoi(cParams);
  return setDigitalListeningState(pin, false);
}

bool handleSrla(const char* cParams, size_t length) {
  int pin = atoi(cParams);
  return setAnalogListeningState(pin, true);
}

bool handleSpla(const char* cParams, size_t length) {
  int pin = atoi(cParams);
  return setAnalogListeningState(pin, false);
}

bool handleCust(const char* cParams, size_t length) {
  String params = String(cParams);
  if (length != UNLIMITED_LENGTH) params = params.substring(0, length);
  int separator = params.indexOf('/');
  if (separator == -1) {
    return handleCustomMessage(params, "", rplyBuffer);
  }
  String customId = params.substring(0, separator);
  String value = params.substring(separator + 1);
  return handleCustomMessage(customId, value, rplyBuffer);
}

const CommandHandler commandHandlers[] = {
    {"ping", noop},
    {"kprs", handleKprs},
    {"ppin", handlePpin},
    {"ppsw", handlePpsw},
    {"tone", handleTone},
    {"notn", handleNotn},
    {"srld", handleSrld},
    {"spld", handleSpld},
    {"srla", handleSrla},
    {"spla", handleSpla},
    {"cust", handleCust}
};

void setup() {
  Serial.begin(115200);
  while (!Serial); // Wait until Serial is connected  

  // Turn off everything (not on RXTX)
  for (int i = 0; i < DIGITAL_PIN_LISTENING_NUM; i++) {
    if (i == 0 || i == 1) continue; // RX/TX
    pinMode(i, OUTPUT);
    digitalWrite(i, LOW);
  }

  Serial.print("alp://info/fw=1.3-snapshot");
  Serial.print(MESSAGE_SEPARATOR_TX);
  Serial.flush();
}

void loop() {
  if (stringComplete) {
    inputBuffer[inputLength] = '\0';  // Null-terminate
    handleInput(inputBuffer);
    inputLength = 0;
    stringComplete = false;
  }

  checkListeningPins();
}

void handleInput(const char* input) {
  if (strncmp(input, "alp://", 6) != 0) return;

  const char* commandAndParams = input + 6;
  const char* idPosition = strstr(commandAndParams, "?id=");

  bool ok = false;

  for (const auto& handler : commandHandlers) {
    size_t commandLength = strlen(handler.command);
    if (strncmp(commandAndParams, handler.command, commandLength) == 0 &&
    (commandAndParams[commandLength] == '/' || commandAndParams[commandLength] == '?' || commandAndParams[commandLength] == '\0')) {
      const char* paramsStart = commandAndParams + commandLength + 1;
      size_t paramLength = idPosition ? (size_t)(idPosition - paramsStart) : UNLIMITED_LENGTH;
      ok = handler.handler(paramsStart, paramLength);
      break;
    }
  }

  if (idPosition) {
    int id = atoi(idPosition + 4); // "?id="
    sendRply(id, ok);
  }
}

void checkListeningPins() {
  for (int i = 0; i < TOTAL_PINS; i++) {
    bool isAnalog = i >= DIGITAL_PIN_LISTENING_NUM;
    int pinIndex = isAnalog ? i - DIGITAL_PIN_LISTENING_NUM : i;

    if (pinListening[i]) {
      int value = isAnalog ? highPrecisionAnalogRead(pinIndex) : digitalRead(pinIndex);

      if (value != pinListenedValue[i]) {
        pinListenedValue[i] = value;
        Serial.print(F("alp://"));
        Serial.print(isAnalog ? F("ared") : F("dred"));
        Serial.print(F("/"));
        Serial.print(pinIndex);
        Serial.print(F("/"));
        Serial.print(value);
        Serial.print(MESSAGE_SEPARATOR_TX);
        Serial.flush();
      }
    }
  }
}

void rplyClear() {
  rplyLength = 0;
  rplyBuffer[0] = '\0';
}

bool rplyAppend(const String& text) {
  return rplyAppend(text.c_str());
}

bool rplyAppend(const char* text) {
  size_t len = strlen(text);
  if (rplyLength + len >= RPLY_BUFFER_SIZE) return false; // prevent overflow
  memcpy(rplyBuffer + rplyLength, text, len);
  rplyLength += len;
  rplyBuffer[rplyLength] = '\0';
  return true;
}

bool rplyAppendInt(int value) {
  char tmp[16];
  itoa(value, tmp, 10);
  return rplyAppend(tmp);
}

void sendRply(int id, bool ok) {
  Serial.print(F("alp://rply/"));
  Serial.print(ok ? F("ok") : F("ko"));
  Serial.print(F("?id="));
  Serial.print(id);

  if (rplyLength > 0) {
    Serial.print(F("&"));
    Serial.print(rplyBuffer);
    rplyClear();
  }

  Serial.print(MESSAGE_SEPARATOR_TX);
  Serial.flush();
}

// Reads 4 times and computes the average value
int highPrecisionAnalogRead(int pin) {
    const int numReadings = 4;
    int sum = 0;
    for (int i = 0; i < numReadings; i++) {
        sum += analogRead(pin);
    }
    return sum / numReadings;
}


/*
 SerialEvent occurs whenever a new data comes in the
 hardware serial RX. This routine is run between each
 time loop() runs, so using delay inside loop can delay
 response. Multiple bytes of data may be available.
 */
void serialEvent() {
  while (Serial.available() && !stringComplete) {
    // get the new byte:
    char inChar = (char)Serial.read();
    // if the incoming character is a newline, set a flag
    // so the main loop can do something about it:
    if (inChar == MESSAGE_SEPARATOR_RX) {
      stringComplete = true;
    } else if (inputLength < INPUT_BUFFER_SIZE - 1) {
      // add it to the inputString:
      inputBuffer[inputLength++] = inChar;
    } else {
      // Too long — discard
      inputLength = 0;
    }
  }
}
