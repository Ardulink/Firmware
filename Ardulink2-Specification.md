# Protocol Specification: Ardulink Protocol (alp://)

## Overview
This protocol enables communication between an Arduino device and a host system over serial communication. It allows the remote control of actuators and monitoring of sensors. Each command follows the format `alp://<command>/<pin>/<value>`, with an optional `?id=<id>` that can be added to the message for tracking individual commands.

- **Note**: The `id=<id>` parameter is **optional** in all commands. If included in the command, it will be included in the response. If no `id` is provided in the command, there will be no response.

## Startup Message
Upon initialization, the Arduino sends an informational message containing key/value pairs. Currently, it includes the firmware version:

`alp://info/fw=1.2`

Additional key/value pairs may be added in the future. This message is sent once when the Arduino starts up and establishes a serial connection.

**Note:** The info message at startup was introduced with firmware version 1.2. In previous versions, only senseless reply message was sent to signal that the Arduino is ready.

## Command Formats

### 1. **Key Press (kprs)**
- **Command**: `alp://kprs/<message>?id=<id>` *(Optional: `?id=<id>`)*  
- **Description**: Sent when a key is pressed.  
- **Parameters**:
  - `message`: The key press message (e.g., "a", "b", etc.).
  - `id`: *(Optional)* Unique message identifier. If provided, it will be included in the response.

### 2. **Power Pin Intensity (ppin)**
- **Command**: `alp://ppin/<pin>/<intensity>?id=<id>` *(Optional: `?id=<id>`)*  
- **Description**: Set the intensity (PWM value) for a power pin.  
- **Parameters**:
  - `pin`: Pin number (integer).
  - `intensity`: PWM intensity value (0-255).
  - `id`: *(Optional)* Unique message identifier. If provided, it will be included in the response.

### 3. **Power Pin Switch (ppsw)**
- **Command**: `alp://ppsw/<pin>/<power>?id=<id>` *(Optional: `?id=<id>`)*  
- **Description**: Set the power state of a pin (ON/OFF).  
- **Parameters**:
  - `pin`: Pin number (integer).
  - `power`: Power state (1 for ON, 0 for OFF).
  - `id`: *(Optional)* Unique message identifier. If provided, it will be included in the response.

### 4. **Tone Request (tone)**
- **Command**: `alp://tone/<pin>/<frequency>/<duration>?id=<id>` *(Optional: `?id=<id>`)*  
- **Description**: Generate a tone on a specified pin.  
- **Parameters**:
  - `pin`: Pin number (integer).
  - `frequency`: Frequency of the tone (Hz).
  - `duration`: Duration of the tone in milliseconds. If -1, the tone will continue indefinitely.
  - `id`: *(Optional)* Unique message identifier. If provided, it will be included in the response.

### 5. **No Tone Request (notn)**
- **Command**: `alp://notn/<pin>?id=<id>` *(Optional: `?id=<id>`)*  
- **Description**: Stop the tone on a specified pin.  
- **Parameters**:
  - `pin`: Pin number (integer).
  - `id`: *(Optional)* Unique message identifier. If provided, it will be included in the response.

### 6. **Start Listen Digital Pin (srld)**
- **Command**: `alp://srld/<pin>?id=<id>` *(Optional: `?id=<id>`)*  
- **Description**: Start listening to a digital pin for state changes.  
- **Parameters**:
  - `pin`: Pin number (integer).
  - `id`: *(Optional)* Unique message identifier. If provided, it will be included in the response.

### 7. **Stop Listen Digital Pin (spld)**
- **Command**: `alp://spld/<pin>?id=<id>` *(Optional: `?id=<id>`)*  
- **Description**: Stop listening to a digital pin.  
- **Parameters**:
  - `pin`: Pin number (integer).
  - `id`: *(Optional)* Unique message identifier. If provided, it will be included in the response.

### 8. **Start Listen Analog Pin (srla)**
- **Command**: `alp://srla/<pin>?id=<id>` *(Optional: `?id=<id>`)*  
- **Description**: Start listening to an analog pin for state changes.  
- **Parameters**:
  - `pin`: Pin number (integer).
  - `id`: *(Optional)* Unique message identifier. If provided, it will be included in the response.

### 9. **Stop Listen Analog Pin (spla)**
- **Command**: `alp://spla/<pin>?id=<id>` *(Optional: `?id=<id>`)*  
- **Description**: Stop listening to an analog pin.  
- **Parameters**:
  - `pin`: Pin number (integer).
  - `id`: *(Optional)* Unique message identifier. If provided, it will be included in the response.

### 10. **Custom Message (cust)**
- **Command**: `alp://cust/<customId>/<value>?id=<id>` *(Optional: `?id=<id>`)*  
- **Description**: Send a custom message to the Arduino.  
- **Parameters**:
  - `customId`: Custom identifier for the message.
  - `value`: The custom message value.
  - `id`: *(Optional)* Unique message identifier. If provided, it will be included in the response.

### 11. **Ping Message (ping)**
- **Command**: `alp://cust/pingid=<id>` *(Optional: `?id=<id>`)*  
- **Description**: Pings the Arduino. Can be used to verify if the Arduino reponds (via id)
- **Parameters**:
  - `id`: *(Optional)* Unique message identifier. If provided, it will be included in the response.

### 12. **Query Analog Pin (qrya)**
- **Command**: `alp://qrya/<pin>?id=<id>` *(Optional: `?id=<id>`)*
- **Description**: Reads an analog pin once without starting a subscription. The pin is configured as `INPUT` for the read. The reply contains the current value in the `value` parameter.
- **Parameters**:
  - `pin`: Analog pin number (integer, e.g. `5` for A5).
  - `id`: *(Optional)* Unique message identifier. If provided, it will be included in the response.

### 13. **Query Digital Pin (qryd)**
- **Command**: `alp://qryd/<pin>?id=<id>` *(Optional: `?id=<id>`)*
- **Description**: Reads a digital pin once without starting a subscription. The pin is configured as `INPUT` for the read. The reply contains the current value (`0` or `1`) in the `value` parameter.
- **Parameters**:
  - `pin`: Pin number (integer).
  - `id`: *(Optional)* Unique message identifier. If provided, it will be included in the response.

---

## Response Format

### 1. **Reply (rply)**
- **Command**: `alp://rply/<status>?id=<id>[&<key>=<value>...]`
- **Description**: The Arduino sends a response back indicating the success or failure of the operation. The response includes the same `id` from the original command (if it was provided). If no `id` was provided in the the original command there will be no reply. Commands may append additional key/value parameters after the `id`, separated by `&`.
- **Parameters**:
  - `status`: "ok" or "ko" indicating whether the command was successful or not.
  - `id`: The unique message identifier that was included in the original command. 
  - `<key>=<value>`: *(Optional)* Additional response data, e.g. `value=987` for `qrya`/`qryd`.

### 2. **Pin Reading**
- **Command**: `alp://<type>/<pin>/<value>`
- **Description**: Sent when a pin's value is read (either digital or analog).  
- **Parameters**:
  - `type`: The type of pin ("dred" for digital or "ared" for analog).
  - `pin`: The pin number that is being monitored.
  - `value`: The value of the pin (either 0/1 for digital or an analog value).

---

## Communication Flow

1. **Host to Arduino**: The host system sends a command to the Arduino.
2. **Arduino Execution**: The Arduino processes the command and interacts with the hardware as necessary.
3. **Arduino to Host**: If the original command contained an `id` the Arduino sends a response with the requests' `id` same. If no `id` was provided in the command, the Arduino will not send a response for that command.

---

## Example Communication

### Case 1: Command with `id`

1. **Command**: `alp://srld/7?id=123`
   - **Description**: Start listening to digital pin 7, with an `id` of "123".
   
2. **Arduino Response**: `alp://rply/ok?id=123`
   - **Description**: Acknowledge the start of pin 7 listening, with the same `id` ("123") to match the original request.

### Case 2: Command without `id`

1. **Command**: `alp://srld/7`
   - **Description**: Start listening to digital pin 7, without an `id`.
   
2. **Arduino Response**: (No response)
   - **Description**: Since the command did not include an `id`, no response is sent from the Arduino.

### Case 3: Query a pin value

1. **Command**: `alp://qrya/5?id=4711`
   - **Description**: Read analog pin A5 once, without starting a subscription.

2. **Arduino Response**: `alp://rply/ok?id=4711&value=123`
   - **Description**: The current value of A5 is `123`.

---

### Key Points

- **`id` is optional** in all commands.
- **If `id` is provided in the command**, the Arduino includes the same `id` in the response.
- **If no `id` is included in the command**, the Arduino does not send a response for that command.
