Feature: SimpleProtocol Behavior

  Scenario: Can switch digital on and off
    Given the pin 12 is digital monitored

    When serial bytes 0x0C 0x0C 0x01 0xFF are sent
    Then the pin 12 should be high

    When serial bytes 0x0C 0x0C 0x00 0xFF are sent
    Then the pin 12 should be low


  Scenario: Can set values on pin
    Given the pin 9 is analog monitored

    When serial bytes 0x0B 0x09 0x7B 0xFF are sent
    Then the pin 9 should be 123

    When serial bytes 0x0B 0x09 0x00 0xFF are sent
    Then the pin 9 should be 0
