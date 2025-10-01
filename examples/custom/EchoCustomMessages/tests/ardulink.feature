Feature: Ardulink Behavior

  Background: Arduino is in steady state
    Given arduino is in steady state

  Scenario: Echo no params and separator at end
    When serial message "alp://cust/doecho/?id=42" is sent
    Then serial response "alp://rply/ok?id=42&response=" was received

  Scenario: Echo no params and no separator at end
    When serial message "alp://cust/doecho?id=43" is sent
    Then serial response "alp://rply/ok?id=43&response=" was received

  Scenario: Echo params
    When serial message "alp://cust/doecho/abc?id=44" is sent
    Then serial response "alp://rply/ok?id=44&response=abc" was received
