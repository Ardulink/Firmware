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
#include <EEPROM.h>

#define UNIQUE_ID_EEPROM_ADDRESS 0
#define UNIQUE_ID_LENGTH 38
#define UNIQUE_ID_MAGIC_NUMBER_HIGH 76
#define UNIQUE_ID_MAGIC_NUMBER_LOW 90

bool handleCustomMessage(String customId, String value) {
//  if (customId == "clearUniqueID") {
//     char buffer[UNIQUE_ID_LENGTH + 1] = { 0 };
//     EEPROM.put(UNIQUE_ID_EEPROM_ADDRESS, buffer);
//     return true;
//  }

   if (customId != "getUniqueID") {
      return false;
   }

   rplyAppend("UniqueID=");
   rplyAppend(getUniqueID(value));
   return true;
}

String getUniqueID(String suggested) {
   char buffer[UNIQUE_ID_LENGTH + 1];

   EEPROM.get(UNIQUE_ID_EEPROM_ADDRESS, buffer);
   if (buffer[0] == UNIQUE_ID_MAGIC_NUMBER_HIGH && buffer[1] == UNIQUE_ID_MAGIC_NUMBER_LOW) {
     // already set
     return String(&buffer[2]);
   }
   // write
   buffer[0] = UNIQUE_ID_MAGIC_NUMBER_HIGH;
   buffer[1] = UNIQUE_ID_MAGIC_NUMBER_LOW;
   suggested.toCharArray(&buffer[2], UNIQUE_ID_LENGTH - 1);
   EEPROM.put(UNIQUE_ID_EEPROM_ADDRESS, buffer);
   return suggested;
}


bool handleKprs(const char* cParams, size_t length) {
  // here you can write your own code. For instance the commented code change pin intensity if you press 'a' or 's'
  // take the command and change intensity on pin 11 this is needed just as example for this sketch
  
  bool commandHandledSuccessfully = false;
  return commandHandledSuccessfully;
}
