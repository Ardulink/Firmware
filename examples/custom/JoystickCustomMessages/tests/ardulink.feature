Feature: Ardulink Behavior

  Background: Arduino is in steady state
    Given arduino is in steady state

  Scenario: Can switch x/y axis via custom message (+x)
    Given the pin 11 is analog monitored
    When serial message "alp://cust/joy/5/7?id=42" is sent
    Then serial response "alp://rply/ok?id=42" was received
    And the pin 11 should be 5

  Scenario: Can switch x/y axis via custom message (-x)
    Given the pin 10 is analog monitored
    When serial message "alp://cust/joy/-5/7?id=42" is sent
    Then serial response "alp://rply/ok?id=42" was received
    And the pin 10 should be 5

  Scenario: Can switch x/y axis via custom message (+y)
    Given the pin 6 is analog monitored
    When serial message "alp://cust/joy/5/7?id=42" is sent
    Then serial response "alp://rply/ok?id=42" was received
    And the pin 6 should be 7

  Scenario: Can switch x/y axis via custom message (-y)
    Given the pin 5 is analog monitored
    When serial message "alp://cust/joy/5/-7?id=42" is sent
    Then serial response "alp://rply/ok?id=42" was received
    And the pin 5 should be 7

  Scenario: Does return ko if message is not joy (text is case sensitive)
    Given the pin 5 is analog monitored
    When serial message "alp://cust/Joy/5/-7?id=42" is sent
    Then serial response "alp://rply/ko?id=42" was received
