Feature: Ardulink Behavior

  Background: Arduino is in steady state
    Given arduino is in steady state

  Scenario: Unknown custom command is not handled
    When serial message "alp://cust/somethingelse?id=1" is sent
    Then serial response "alp://rply/ko?id=1" was received

  Scenario: First request writes the suggested id to EEPROM
    When serial message "alp://cust/getUniqueID/DeviceAlpha?id=2" is sent
    Then serial response "alp://rply/ok?id=2&UniqueID=DeviceAlpha" was received

  Scenario: Later requests return the id stored in EEPROM
    When serial message "alp://cust/getUniqueID/DeviceAlpha?id=3" is sent
    Then serial response "alp://rply/ok?id=3&UniqueID=DeviceAlpha" was received
    When serial message "alp://cust/getUniqueID/OtherSuggestion?id=4" is sent
    Then serial response "alp://rply/ok?id=4&UniqueID=DeviceAlpha" was received

  Scenario: Stored id survives further suggestions
    When serial message "alp://cust/getUniqueID/DeviceAlpha?id=5" is sent
    Then serial response "alp://rply/ok?id=5&UniqueID=DeviceAlpha" was received
    When serial message "alp://cust/getUniqueID/DeviceBeta?id=6" is sent
    Then serial response "alp://rply/ok?id=6&UniqueID=DeviceAlpha" was received
    When serial message "alp://cust/getUniqueID/DeviceGamma?id=7" is sent
    Then serial response "alp://rply/ok?id=7&UniqueID=DeviceAlpha" was received
