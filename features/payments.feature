Feature: The payments service back-end
    As a Payments Manager
    I need a RESTful catalog service
    So that I can keep track of all the payments

Background:
    Given the following payments
    | id | customer_id | order_id | payment_method_type | payment_status | default_payment_type |
    |  1 | 12302       | 11150    | CREDIT              | PAID           | False                |
    |  2 | 12302       | 12143    | DEBIT               | PAID           | False                |
    |  3 | 14121       | 11122    | CREDIT              | PAID           | False                |
    |  4 | 14121       | 15189    | PAYPAL              | PROCESSING     | False                |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Payments REST API Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Payment
    When I visit the "Home Page"
    And I set the "customer_id" to 12302
    And I set the "order_id" to 11121
    And I set the "payment_method_type" to "DEBIT"
    And I set the "payment_status" to "PAID"
    And I set the "default_payment_type" to False
    And I press the "Create" button
    Then I should see the message "Success"
