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