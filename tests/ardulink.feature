Feature: Ardulink Behavior

  Background: Arduino is in steady state
    Given arduino is in steady state

    
  Scenario: Can ping Arduino
    When serial message "alp://ping?id=123" is sent
    Then serial response "alp://rply/ok?id=123" was received


  Scenario: Can switch digital on and off
    Given the pin D12 is digital monitored

    When serial message "alp://ppsw/12/1" is sent
    Then the pin D12 should be high

    When serial message "alp://ppsw/12/0" is sent
    Then the pin D12 should be low


  Scenario: Can set values on pin
    Given the pin D9 is analog monitored

    When serial message "alp://ppin/9/123" is sent
    Then the pin D9 should be 123

    When serial message "alp://ppin/9/0" is sent
    Then the pin D9 should be 0


  Scenario: Tone without rply message
    Given the pin D9 is analog monitored

    When serial message "alp://tone/9/123/-1" is sent
    Then the pin D9 should be 127

    When serial message "alp://notn/9" is sent
    Then the pin D9 should be 0


  Scenario: Tone with rply message
    Given the pin D9 is analog monitored

    When serial message "alp://tone/9/123/-1?id=42" is sent
    And serial response "alp://rply/ok?id=42" was received
    Then the pin D9 should be 127

    When serial message "alp://notn/9?id=43" is sent
    And serial response "alp://rply/ok?id=43" was received
    Then the pin D9 should be 0


  Scenario: Custom messages are not supported in default implementation
    When serial message "alp://cust/abc/xyz?id=42" is sent
    Then serial response "alp://rply/ko?id=42" was received


  Scenario: Keypress messages are not supported in default implementation
    When serial message "alp://kprs/xxxx?id=42" is sent
    Then serial response "alp://rply/ko?id=42" was received


  Scenario: Unknown command result in ko rply
    When serial message "alp://XXXX/123/abc/X-Y-Z?id=42" is sent
    Then serial response "alp://rply/ko?id=42" was received


  Scenario: Can read analog pin state initial pin state 0
    When serial message "alp://srla/5?id=42" is sent
    Then serial response "alp://rply/ok?id=42" was received
    And serial response "alp://ared/5/0" was received

    When the pin A5 is set to 987
    Then serial response "alp://ared/5/987" was received

    When serial message "alp://spla/5?id=43" is sent
    Then serial response "alp://rply/ok?id=43" was received


  Scenario: Can read analog pin state initial pin state 987
    Given the pin A5 is set to 987
    When serial message "alp://srla/5?id=42" is sent
    Then serial response "alp://rply/ok?id=42" was received
    And serial response "alp://ared/5/987" was received

    When serial message "alp://spla/5?id=43" is sent
    Then serial response "alp://rply/ok?id=43" was received


  Scenario: Can read digital pin state initial pin state 0
    When serial message "alp://srld/12?id=42" is sent
    Then serial response "alp://rply/ok?id=42" was received
    And serial response "alp://dred/12/0" was received

    When the pin D12 is set to high
    And serial response "alp://dred/12/1" was received

    When serial message "alp://spld/12?id=43" is sent
    Then serial response "alp://rply/ok?id=43" was received


  Scenario: Can read digital pin state initial pin state 1
    Given the pin D12 is set to high
    When serial message "alp://srld/12?id=42" is sent
    Then serial response "alp://rply/ok?id=42" was received
    And serial response "alp://dred/12/1" was received

    When serial message "alp://spld/12?id=43" is sent
    Then serial response "alp://rply/ok?id=43" was received
