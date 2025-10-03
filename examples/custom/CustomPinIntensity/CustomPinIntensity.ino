#define LED_PIN 11
#define CHAR_AT 3

#define MIN_INTENSITY 0
#define MAX_INTENSITY 127

struct Command { char code; int delta; };
const Command commands[] = {
  {'s', +1},
  {'a', -1}
};
const size_t commandCount = sizeof(commands) / sizeof(commands[0]);

static int intensity = 0;

bool handleCustomMessage(String customId, String value) {
  // here you can write your own code. 
  bool commandHandledSuccessfully = false;
  return commandHandledSuccessfully;
}

bool handleKprs(const char* cParams, size_t length) {
  if (length > CHAR_AT) {
    const char commandChar = cParams[CHAR_AT];
    for (size_t i = 0; i < commandCount; ++i) {
      if (commands[i].code == commandChar) {
        intensity = constrain(intensity + commands[i].delta, MIN_INTENSITY, MAX_INTENSITY);
        analogWrite(LED_PIN, intensity);
        return true;
      }
    }
  }
  return false;
}
