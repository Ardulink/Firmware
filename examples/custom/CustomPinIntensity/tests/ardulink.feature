Feature: Ardulink Behavior

  Background: Arduino is in steady state
    Given arduino is in steady state

  Scenario: Three times pressing s results in pin value 3
    Given the pin D11 is analog monitored
    When serial message "alp://kprs/xxxs?id=42" is sent
    Then serial response "alp://rply/ok?id=42" was received
    When serial message "alp://kprs/xxxs?id=43" is sent
    Then serial response "alp://rply/ok?id=43" was received
    When serial message "alp://kprs/xxxs?id=44" is sent
    Then serial response "alp://rply/ok?id=44" was received
    And the pin D11 should be 3

  Scenario: Three times pressing s and three times pressing a results in pin value 0
    Given the pin D11 is analog monitored
    When serial message "alp://kprs/xxxs?id=42" is sent
    Then serial response "alp://rply/ok?id=42" was received
    When serial message "alp://kprs/xxxs?id=43" is sent
    Then serial response "alp://rply/ok?id=43" was received
    When serial message "alp://kprs/xxxs?id=44" is sent
    Then serial response "alp://rply/ok?id=44" was received
    When serial message "alp://kprs/xxxa?id=45" is sent
    Then serial response "alp://rply/ok?id=45" was received
    When serial message "alp://kprs/xxxa?id=46" is sent
    Then serial response "alp://rply/ok?id=46" was received
    When serial message "alp://kprs/xxxa?id=47" is sent
    Then serial response "alp://rply/ok?id=47" was received
    And the pin D11 should be 0

  Scenario: Does return ko if key is not a or s
    When serial message "alp://ḱprs/xxxy?id=42" is sent
    Then serial response "alp://rply/ko?id=42" was received

