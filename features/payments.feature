Feature: The payments service back-end
    As a Payments Manager
    I need a RESTful catalog service
    So that I can keep track of all the payments

Background:
    Given the following payments
    | id | customer_id | order_id | payment_method_type | payment_status | default_payment_type |
    |  1 | 12302       | 11150    | CREDIT              | PAID           | false                |
    |  2 | 12302       | 12143    | DEBIT               | PAID           | false                |
    |  3 | 14121       | 11122    | CREDIT              | PAID           | false                |
    |  4 | 14121       | 15189    | PAYPAL              | PROCESSING     | false                |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Payments REST API Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Payment
    When I visit the "Home Page"
    And I set the "id" to "5"
    And I set the "customer_id" to "12302"
    And I set the "order_id" to "11121"
    And I set the "payment_method_type" to "CREDIT"
    And I set the "payment_status" to "PROCESSING"
    And I press the "Create" button
    Then I should see the message "Success - Payment Added!"


Scenario: List all payments
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "11150" in the results
    And I should see "12143" in the results
    And I should see "11122" in the results
    And I should see "15189" in the results


Scenario: List all payments by customer_id
    When I visit the "Home Page"
    And I set the "customer_id" to "12302"
    And I press the "Search" button
    Then I should see "11150" in the results
    And I should see "12143" in the results
    And I should not see "11122" in the results
    And I should not see "15189" in the results

Scenario: List all payments by payment_method_type
    When I visit the "Home Page"
    And I set the "payment_method_type" to "CREDIT"
    And I press the "Search" button
    Then I should see "11150" in the results
    And I should see "11122" in the results
    And I should not see "12143" in the results
    And I should not see "15189" in the results


Scenario: List all payments by payment_status
    When I visit the "Home Page"
    And I set the "payment_status" to "PROCESSING"
    And I press the "Search" button
    Then I should see "15189" in the results
    And I should not see "12143" in the results
    And I should not see "11122" in the results
    And I should not see "11150" in the results


Scenario: List all payments by order_id
    When I visit the "Home Page"
    And I set the "order_id" to "11150"
    And I press the "Search" button
    Then I should see "11150" in the results
    And I should not see "12143" in the results
    And I should not see "11122" in the results
    And I should not see "15189" in the results


Scenario: Create a Payment
    When I visit the "Home Page"
    And I set the "id" to "6"
    And I set the "customer_id" to "12302"
    And I set the "order_id" to "11123"
    And I set the "payment_method_type" to "DEBIT"
    And I set the "payment_status" to "PROCESSING"
    And I press the "Create" button
    Then I should see the message "Success - Payment Added!"


Scenario: Update a payment
    When I visit the "Home Page"
    And I set the "id" to "4"
    And I press the "Retrieve" button
    Then I should see "PROCESSING" in the "payment_status" field
    When I set the "payment_status" to "PAID"
    And I press the "Update" button
    Then I should see the message "Success"
    When I set the "id" to "4"
    And I press the "Retrieve" button
    Then I should see "PAID" in the "payment_status" field


Scenario: Delete a Payment
    When I visit the "Home Page"
    And I set the "id" to "6"
    And I press the "Delete" button
    Then I should see the message "Payment with ID [6] has been Deleted!"

Scenario: Set Default Payment Resource
    When I visit the "Home Page"
    And I set the "id" to "3"
    And I press the "Set Default Payment Method" button
    Then I should see the message "Payment with ID [3] has been set as Default Payment Resource!"
