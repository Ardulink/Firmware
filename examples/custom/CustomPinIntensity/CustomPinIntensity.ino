#define LED_PIN 11
#define CHAR_AT 3

bool handleCustomMessage(String customId, String value) {
  // here you can write your own code. 
  bool commandHandledSuccessfully = false;
  return commandHandledSuccessfully;
}

bool handleKprs(const char* cParams, size_t length) {
  static int intensity = 0;

  if (length < CHAR_AT + 1) {
    return false;
  }
  char commandChar = cParams[CHAR_AT];
  if (commandChar == 'a') {
    // If press 'a' less intensity
    intensity = max(0, intensity - 1);
    analogWrite(LED_PIN, intensity);
    return true;
  } else if (commandChar == 's') {
    // If press 's' more intensity
    intensity = min(127, intensity + 1);
    analogWrite(LED_PIN, intensity);
    return true;
  }
  return false;
}
