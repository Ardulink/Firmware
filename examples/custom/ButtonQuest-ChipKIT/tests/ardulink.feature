Feature: Button game with IOShieldOled

  Background: Arduino is in steady state
    Given arduino is in steady state

  Scenario: Correct combination of buttons
    Given serial message "alp://cust/setbutton/on/1?id=1" is sent
    And serial response "alp://rply/ok?id=1" was received
    And serial message "alp://cust/setbutton/on/3?id=2" is sent
    And serial response "alp://rply/ok?id=2" was received
    And the pin D35 is set to HIGH
    And the pin D7 is set to HIGH
    And the pin D8 is set to LOW
    And the pin D2 is set to LOW
    When serial message "alp://cust/getResult?id=3" is sent
    Then serial response "alp://rply/ok?id=3" was received
    And serial response contains "RIGHT!"

  Scenario: Wrong combination of buttons
    Given serial message "alp://cust/setbutton/on/2?id=4" is sent
    And serial response "alp://rply/ok?id=4" was received
    And serial message "alp://cust/setbutton/on/4?id=5" is sent
    And serial response "alp://rply/ok?id=5" was received
    And the pin D8 is set to HIGH
    And the pin D2 is set to LOW   # expected HIGH but actually LOW
    And the pin D35 is set to LOW
    And the pin D7 is set to LOW
    When serial message "alp://cust/getResult?id=6" is sent
    Then serial response "alp://rply/ok?id=6" was received
    And serial response contains "WRONG!"

  Scenario Outline: Single button expectations
    Given serial message "alp://cust/setbutton/on/<button>?id=<id>" is sent
    And serial response "alp://rply/ok?id=<id>" was received
    And the pin <pin> is set to <state>
    When serial message "alp://cust/getResult?id=<id2>" is sent
    Then serial response "alp://rply/ok?id=<id2>" was received
    And serial response contains "<result>"

    Examples:
      | button | pin | state | id | id2 | result  |
      | 1      | D35 | HIGH  | 10 | 11  | RIGHT!  |
      | 2      | D8  | LOW   | 12 | 13  | WRONG!  |
      | 3      | D7  | HIGH  | 14 | 15  | RIGHT!  |
      | 4      | D2  | LOW   | 16 | 17  | WRONG!  |
