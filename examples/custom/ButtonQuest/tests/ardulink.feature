Feature: Button game with OLED

  Background: Arduino is in steady state and expected buttons configured
    Given arduino is in steady state
    When serial message "alp://cust/setbutton/on/1" is sent
    When serial message "alp://cust/setbutton/on/4" is sent

  Scenario: Correct combination of buttons
    When the pin D3 is set to high
    And the pin D2 is set to high
    And serial message "alp://cust/getResult/?id=3" is sent
    Then serial response matches "^alp:\/\/rply\/ok\?id=3.*RIGHT!$"

  Scenario: Wrong combination of buttons
    When the pin D3 is set to high
    And serial message "alp://cust/getResult/?id=3" is sent
    Then serial response matches "^alp:\/\/rply\/ok\?id=3.*WRONG!$"
