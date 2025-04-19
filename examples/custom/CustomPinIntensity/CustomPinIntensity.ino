#define LED_PIN 11
#define CHAR_AT 3

bool handleCustomMessage(String customId, String value) {
  // here you can write your own code. 
  bool commandHandledSuccessfully = false;
  return commandHandledSuccessfully;
}

bool handleKprs(const char* cParams, size_t length) {
  if (length > CHAR_AT) {
    char commandChar = cParams[CHAR_AT];
    if (commandChar == 's') {
      // If press 's' more intensity
      return adjustIntensity(+1);
    }
    if (commandChar == 'a') {
      // If press 'a' less intensity
      return adjustIntensity(-1);
    }
  }
  return false;
}

bool adjustIntensity(int delta) {
  static int intensity = 0;
  analogWrite(LED_PIN, intensity = constrain(intensity + delta, 0, 127));
  return true;
}
