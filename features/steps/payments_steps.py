"""
Payments Steps
Steps file for payments.feature
"""
from os import getenv
import json
import requests
from behave import *
from compare import expect, ensure
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions

# WAIT_SECONDS = 30
BASE_URL = getenv('BASE_URL', 'http://localhost:5000/')


@given('the following payments')
def step_impl(context):
    """ Delete all Payments and load new ones """
    headers = {'Content-Type': 'application/json'}
    context.resp = requests.delete(context.base_url + '/payments/reset', headers=headers)
    expect(context.resp.status_code).to_equal(204)
    create_url = context.base_url + '/payments'
    for row in context.table:
        data = {
            "id": row['id'],
            "customer_id": row['customer_id'],
            "order_id": row['order_id'],
            "payment_method_type": row['payment_method_type'],
            "payment_status": row['payment_status'],
            "default_payment_type": row['default_payment_type'] in ['False', 'false', '1']
            }
        payload = json.dumps(data)
        context.resp = requests.post(create_url, data=payload, headers=headers)
        expect(context.resp.status_code).to_equal(201)

@when('I visit the "home page"')
def step_impl(context):
    """ Make a call to the base URL """
    context.driver.get(context.base_url)
    #context.driver.save_screenshot('home_page.png')

@then('I should see "{message}" in the title')
def step_impl(context, message):
    """ Check the document title for a message """
    print("context.driver.title")
    print(context.driver.title)
    expect(context.driver.title).to_contain(message)

@then('I should not see "{message}"')
def step_impl(context, message):
    error_msg = "I should not see '%s' in '%s'" % (message, context.resp.text)
    ensure(message in context.resp.text, False, error_msg)
