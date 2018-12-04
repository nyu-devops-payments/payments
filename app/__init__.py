"""
Package: app

Package for the application models and services
This module also sets up the logging to be used with gunicorn
"""
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import sqlalchemy
from sqlalchemy import *

# Create Flask application
app = Flask(__name__)

import service

# Set up logging for production
print 'Setting up logging for {}...'.format(__name__)
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    if gunicorn_logger:
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)

# Load the confguration
app.config.from_object('config')
# Initialize SQLAlchemy
db = SQLAlchemy(app)
#db = sqlalchemy.create_engine('ibm_db_sa://db2inst1:secret@host.name.com:50000/pydev')

app.logger.info('Logging established')
