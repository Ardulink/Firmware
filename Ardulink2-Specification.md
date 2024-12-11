# Protocol Specification: Ardulink Protocol (alp://)

## Overview
This protocol enables communication between an Arduino device and a host system over serial communication. It allows the remote control of actuators and monitoring of sensors. Each command follows the format `alp://<command>/<pin>/<value>`, with an optional `?id=<id>` that can be added to the message for tracking individual commands.

- **Note**: The `id=<id>` parameter is **optional** in all commands. If included in the command, it will be included in the response. If no `id` is provided in the command, there will be no response.

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

---

## Response Format

### 1. **Reply (rply)**
- **Command**: `alp://rply/<status>?id=<id>`  
- **Description**: The Arduino sends a response back indicating the success or failure of the operation. The response includes the same `id` from the original command (if it was provided).  
- **Parameters**:
  - `status`: "ok" or "ko" indicating whether the command was successful or not.
  - `id`: *(Optional)* The unique message identifier that was included in the original command (if provided). This `id` **must** be included in the response if the original command contained an `id`. If the command did not include an `id`, the response will not include an `id`.

### 2. **Pin Reading**
- **Command**: `alp://<type>/<pin>/<value>`
- **Description**: Sent when a pin's value is read (either digital or analog).  
- **Parameters**:
  - `type`: The type of pin ("dred" for digital or "ared" for analog).
  - `pin`: The pin number that is being monitored.
  - `value`: The value of the pin (either 0/1 for digital or an analog value).
  - `id`: *(Optional)* Unique message identifier. If the original command had an `id`, it will be included in the response.

---

## Communication Flow

1. **Host to Arduino**: The host system sends a command to the Arduino.
2. **Arduino Execution**: The Arduino processes the command and interacts with the hardware as necessary.
3. **Arduino to Host**: The Arduino sends a response. If the original command contained an `id`, it will be included in the response. If no `id` was provided in the command, the Arduino will not send an `id` in the response.

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

---

### Key Points

- **`id` is optional** in all commands.
- **If `id` is provided in the command**, the Arduino includes the same `id` in the response.
- **If no `id` is included in the command**, the Arduino does not send any response at all.
