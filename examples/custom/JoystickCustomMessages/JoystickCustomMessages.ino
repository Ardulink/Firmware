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
#define X_AXIS_FWD 11
#define X_AXIS_REW 10
#define Y_AXIS_FWD  6
#define Y_AXIS_REW  5

bool handleCustomMessage(String customId, String value) {        
  if (customId != "joy") {
    return false;
  }

  int separatorXYPosition = value.indexOf('/');
  int x = value.substring(0, separatorXYPosition).toInt();
  int y = value.substring(separatorXYPosition + 1).toInt();

  const bool xFwd = x >= 0;
  const bool yFwd = y >= 0;
  analogWrite(xFwd ? X_AXIS_FWD : X_AXIS_REW, abs(x));
  analogWrite(xFwd ? X_AXIS_REW : X_AXIS_FWD, 0);
  analogWrite(yFwd ? Y_AXIS_FWD : Y_AXIS_REW, abs(y));
  analogWrite(yFwd ? Y_AXIS_REW : Y_AXIS_FWD, 0);

  return true;
}

bool handleKprs(const char* cParams, size_t length) {
  // here you can write your own code. For instance the commented code change pin intensity if you press 'a' or 's'
  // take the command and change intensity on pin 11 this is needed just as example for this sketch
  
  bool commandHandledSuccessfully = false;
  return commandHandledSuccessfully;
}
