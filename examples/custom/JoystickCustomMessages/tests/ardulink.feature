Feature: Ardulink Behavior

  Background: Arduino is in steady state
    Given arduino is in steady state

  Scenario: Can switch x/y axis via custom message (+x)
    Given the pin D11 is analog monitored
    When serial message "alp://cust/joy/5/7?id=42" is sent
    Then serial response "alp://rply/ok?id=42" was received
    And the pin D11 should be 5

  Scenario: Can switch x/y axis via custom message (-x)
    Given the pin D10 is analog monitored
    When serial message "alp://cust/joy/-5/7?id=42" is sent
    Then serial response "alp://rply/ok?id=42" was received
    And the pin D10 should be 5

  Scenario: Can switch x/y axis via custom message (+y)
    Given the pin D6 is analog monitored
    When serial message "alp://cust/joy/5/7?id=42" is sent
    Then serial response "alp://rply/ok?id=42" was received
    And the pin D6 should be 7

  Scenario: Can switch x/y axis via custom message (-y)
    Given the pin D5 is analog monitored
    When serial message "alp://cust/joy/5/-7?id=42" is sent
    Then serial response "alp://rply/ok?id=42" was received
    And the pin D5 should be 7
