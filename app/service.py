"""
Payments Microservice
Paths:
------
GET /cards - Returns a list all of the Cards
GET /cards/{id} - Returns the Card with a given id number
POST /cards - creates a new Card record in the database
PUT /cards/{id} - updates a Card record in the database
DELETE /cards/{id} - deletes a Card record in the database
"""


import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from flask_api import status    # HTTP Status Codes
from werkzeug.exceptions import NotFound

# We use SQLAlchemy that supports SQLite, MySQL and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from models import Card, DataValidationError

# Import Flask application
from . import app

######################################################################
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    return bad_request(error)

@app.errorhandler(400)
def bad_request(error):
    """ Handles bad reuests with 400_BAD_REQUEST """
    message = error.message or str(error)
    app.logger.info(message)
    return jsonify(status=400, error='Bad Request', message=message), 400

@app.errorhandler(404)
def not_found(error):
    """ Handles resources not found with 404_NOT_FOUND """
    message = error.message or str(error)
    app.logger.info(message)
    return jsonify(status=404, error='Not Found', message=message), 404

@app.errorhandler(405)
def method_not_supported(error):
    """ Handles unsuppoted HTTP methods with 405_METHOD_NOT_SUPPORTED """
    message = error.message or str(error)
    app.logger.info(message)
    return jsonify(status=405, error='Method not Allowed', message=message), 405

@app.errorhandler(415)
def mediatype_not_supported(error):
    """ Handles unsuppoted media requests with 415_UNSUPPORTED_MEDIA_TYPE """
    message = error.message or str(error)
    app.logger.info(message)
    return jsonify(status=415, error='Unsupported media type', message=message), 415

@app.errorhandler(500)
def internal_server_error(error):
    """ Handles unexpected server error with 500_SERVER_ERROR """
    message = error.message or str(error)
    app.logger.info(message)
    return jsonify(status=500, error='Internal Server Error', message=message), 500


######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    """ Root URL response """
    return jsonify(name='Payments REST API Service',
                   version='1.0',
                   paths=url_for('list_cards', _external=True)
                  ), status.HTTP_200_OK

######################################################################
# LIST ALL CARDS
######################################################################
@app.route('/cards', methods=['GET'])
def list_cards():
    """ Returns all of the Cards """
    cards = []
    number = request.args.get('number')
    exp_year = request.args.get('exp_year')
    name = request.args.get('ch_name')
    if exp_year:
        cards = Card.find_by_exp_year(exp_year)
    elif number:
        cards = Card.find_by_number(number)
    elif name:
        cards = Card.find_by_name(ch_name)         # Name on Card should be added - #Done
    else:
        cards = Card.all()

    results = [card.serialize() for card in cards]
    return make_response(jsonify(results), status.HTTP_200_OK)


######################################################################
# RETRIEVE A SINGLE CARD
######################################################################
@app.route('/cards/<string:number>', methods=['GET'])
def get_cards(number):
    """
    Retrieves a single Card for a customer

    This endpoint will return a Card based on it's number
    """
    card = Card.find(number)
    if not card:
        raise NotFound("Card Number '{}' was not found.".format(number))
    return make_response(jsonify(card.serialize()), status.HTTP_200_OK)


######################################################################
# ADD A NEW Card
######################################################################
@app.route('/cards', methods=['POST'])
def create_cards():
    """
    Creates a Card
    This endpoint will create a Payment source based on the Card Info in the body that is posted
    """
    check_content_type('application/json')
    card = Card()
    card.deserialize(request.get_json())
    card.save()
    message = card.serialize()
    location_url = url_for('get_cards', card_id=card.id, _external=True)
    return make_response(jsonify(message), status.HTTP_201_CREATED,
                         {
                             'Location': location_url
                         })

######################################################################
# UPDATE AN EXISTING CARD
######################################################################
@app.route('/cards/<int:card_id>', methods=['PUT'])
def update_cards(card_id):
    """
    Update a Card
    This endpoint will update a Card based the body that is posted
    """
    check_content_type('application/json')
    card = Card.find(card_id)
    if not card:
        raise NotFound("Card with id '{}' was not found.".format(card_id))
    card.deserialize(request.get_json())
    card.id = card_id
    card.save()
    return make_response(jsonify(card.serialize()), status.HTTP_200_OK)


######################################################################
# DELETE A CARD
######################################################################
@app.route('/cards/<int:card_id>', methods=['DELETE'])
def delete_cards(card_id):
    """
    Delete a Card
    This endpoint will delete a Card based the id specified in the path
    """
    card = Card.find(card_id)
    if card:
        card.delete()
    return make_response('', status.HTTP_204_NO_CONTENT)

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    Card.init_db(app)

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers['Content-Type'] == content_type:
        return
    app.logger.error('Invalid Content-Type: %s', request.headers['Content-Type'])
    abort(415, 'Content-Type must be {}'.format(content_type))

def initialize_logging(log_level=logging.INFO):
    """ Initialized the default logging to STDOUT """
    if not app.debug:
        print 'Setting up logging...'
        # Set up default logging for submodules to use STDOUT
        # datefmt='%m/%d/%Y %I:%M:%S %p'
        fmt = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        logging.basicConfig(stream=sys.stdout, level=log_level, format=fmt)
        # Make a new log handler that uses STDOUT
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt))
        handler.setLevel(log_level)
        # Remove the Flask default handlers and use our own
        handler_list = list(app.logger.handlers)
        for log_handler in handler_list:
            app.logger.removeHandler(log_handler)
        app.logger.addHandler(handler)
        app.logger.setLevel(log_level)
        app.logger.info('Logging handler established')
