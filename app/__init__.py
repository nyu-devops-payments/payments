# Copyright 2016, 2017 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Microservice module

This module contains the microservice code for
    service
    models
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import ibm_db_sa

# These next lines are positional:
# 1) We need to create the Flask app
# 2) Then configure it
# 3) Then initialize SQLAlchemy after it has been configured

app = Flask(__name__)
# Load the confguration
with app.app_context():
    app.config.from_object('config')
    app.logger.debug('Database URI {}'.format(app.config['SQLALCHEMY_DATABASE_URI']))

# Initialize SQLAlchemy
db = SQLAlchemy(app)

from app import service, models




#############  EARLIER VERSION FOR SQL-ALCHEMY ####################
# """
# Package: app
#
# Package for the application models and services
# This module also sets up the logging to be used with gunicorn
# """
# import logging
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
#
# import sqlalchemy
# from sqlalchemy import *
#
# # Create Flask application
# app = Flask(__name__)
#
# import service
#
# # Set up logging for production
# print 'Setting up logging for {}...'.format(__name__)
# if __name__ != '__main__':
#     gunicorn_logger = logging.getLogger('gunicorn.error')
#     if gunicorn_logger:
#         app.logger.handlers = gunicorn_logger.handlers
#         app.logger.setLevel(gunicorn_logger.level)
#
# # Load the confguration
# app.config.from_object('config')
# # Initialize SQLAlchemy
# db = SQLAlchemy(app)
# #db = sqlalchemy.create_engine('ibm_db_sa://db2inst1:secret@host.name.com:50000/pydev')
#
# app.logger.info('Logging established')
###################################################################
