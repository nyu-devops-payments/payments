"""
Environment for Behave Testing
"""
import os
from behave import *
from selenium import webdriver

WAIT_SECONDS = 120
<<<<<<< HEAD
#BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')
BASE_URL = os.getenv('BASE_URL', 'https://nyu-payment-service-f18.mybluemix.net')

=======
BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')
# BASE_URL = os.getenv('BASE_URL', 'https://nyu-payment-service-f18.mybluemix.net')
>>>>>>> b50318b248447adfe22d0ae0e92cce7f220c15c0

def before_all(context):
    """ Executed once before all tests """
    context.driver = webdriver.PhantomJS()
    # context.driver.manage().timeouts().pageLoadTimeout(WAIT_SECONDS, TimeUnit.SECONDS);
    # context.driver.manage().timeouts().setScriptTimeout(WAIT_SECONDS, TimeUnit.SECONDS);
    context.driver.implicitly_wait(WAIT_SECONDS) # seconds
    context.driver.set_window_size(1120, 550)
    context.base_url = BASE_URL
    # -- SET LOG LEVEL: behave --logging-level=ERROR ...
    # on behave command-line or in "behave.ini"
    context.config.setup_logging()
