Feature: Ardulink Behavior

  Background: Arduino is in steady state
    Given arduino is in steady state
    And the pin D11 is digital monitored
    And the pin D12 is digital monitored

  Scenario: Echo no params and separator at end
    When serial message "alp://cust/doecho/?id=42" is sent
    Then serial response "alp://rply/ok?id=42&response=" was received
    And the pin D11 should be 1

  Scenario: Echo no params and no separator at end
    When serial message "alp://cust/doecho?id=43" is sent
    Then serial response "alp://rply/ok?id=43&response=" was received
    And the pin D11 should be 1

  Scenario: Echo params
    When serial message "alp://cust/doecho/abc?id=44" is sent
    Then serial response "alp://rply/ok?id=44&response=abc" was received
    And the pin D11 should be 1

  Scenario: ko if command is not exactly "doecho"
    When serial message "alp://cust/doEcho/abc?id=45" is sent
    Then serial response "alp://rply/ko?id=45" was received
    And the pin D12 should be 1

  Scenario: no-id: Echo no params and separator at end
    When serial message "alp://cust/doecho/" is sent
    Then the pin D11 should be 1

  Scenario: no-id: Echo no params and no separator at end
    When serial message "alp://cust/doecho" is sent
    Then the pin D11 should be 1

  Scenario: no-id: Echo params
    When serial message "alp://cust/doecho/abc" is sent
    Then the pin D11 should be 1

  Scenario: no-id: ko if command is not exactly "doecho"
    When serial message "alp://cust/doEcho/abc" is sent
    Then the pin D12 should be 1
