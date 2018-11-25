"""
Payments Microservice API

URLs:
------
GET /payments - Returns a list of all Payments of all customers
GET /payments/{id} - Returns the Payment with a given id number
POST /payments - creates a new Payment record in database
PUT /payments/{order_id} - updates a Payment record in database
DELETE /payments/{id} - deletes a Payment record in database
"""


import os
import sys
import logging
import make_enum_json_serializable  # ADDED
from flask import Flask, jsonify, request, url_for, make_response, abort
from flask_api import status    # HTTP Status Codes
from werkzeug.exceptions import NotFound

# We use SQLAlchemy that supports SQLite, MySQL and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from models import Payment, PaymentMethodType, PaymentStatus, DataValidationError


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
                   paths=url_for('list_payments', _external=True)
                  ), status.HTTP_200_OK

######################################################################
# LIST ALL PAYMENTS
######################################################################
@app.route('/payments', methods=['GET'])
def list_payments():
    """ Returns all Payments of all Customers """
    payments = []
    customer_id = request.args.get('customer_id')
    order_id = request.args.get('order_id')
    payment_method_type = request.args.get('payment_method_type')
    payment_status = request.args.get('payment_status')

    if customer_id:
        payments = Payment.find_by_customer_id(customer_id)
    elif order_id:
        payments = Payment.find_by_order_id(order_id)
    elif payment_method_type:
        payments = Payment.find_by_payment_method_type(payment_method_type)
    elif payment_status:
        payments = Payment.find_by_payment_status(payment_status)
    else:
        payments = Payment.all()

    results = [payment.serialize() for payment in payments]
    return make_response(jsonify(results), status.HTTP_200_OK)



######################################################################
# RETRIEVES A SINGLE PAYMENT  ---
#####################################################################
@app.route('/payments/<int:id>', methods=['GET'])
def get_payments(id):
    """
    Retrieves a single Payment for the customer
    This endpoint will return a Payment based on it's id
    """

    payment = Payment.find(id)
    if not payment:
        raise NotFound("Payment '{}' was not found.".format(id))
    return make_response(jsonify(payment.serialize()), status.HTTP_200_OK)


######################################################################
# ADDS A NEW PAYMENT
######################################################################
@app.route('/payments', methods=['POST'])
def create_payments():
    """
    Creates a Payment Method
    This endpoint will create a Payment source based on the Payment Info in the body that is posted
    """
    check_content_type('application/json')
    payment = Payment()
    payment.deserialize(request.get_json())
    payment.save()
    message = payment.serialize()
    location_url = url_for('get_payments', id=payment.id, _external=True)
    return make_response(jsonify(message), status.HTTP_201_CREATED,
                         {
                             'Location': location_url
                         })

######################################################################
# UPDATE AN EXISTING PAYMENT   --- TODO #1 (Varsha)
######################################################################
@app.route('/payments/<int:id>', methods=['PUT'])
def update_payments(id):
    """
    Update a Card
    This endpoint will update a Payment resource based on the Payment Info in the body that is posted
    """
    check_content_type('application/json')
    payment = Payment.find(id)
    if not payment:
        raise NotFound("Payment '{}' was not found.".format(id))
    payment.deserialize(request.get_json())
    payment.save()
    message = payment.serialize()
    return make_response(jsonify(message), status.HTTP_200_OK)


######################################################################
# DELETE A PAYMENT   --- TODO #2 (Shu)
######################################################################
# @app.route('/cards/<int:card_id>', methods=['DELETE'])
# def delete_cards(card_id):
#     """
#     Delete a Card
#     This endpoint will delete a Card based the id specified in the path
#     """
#     card = Card.find(card_id)
#     if card:
#         card.delete()
#     return make_response('', status.HTTP_204_NO_CONTENT)


######################################################################
#   PERFORM ACTIONS - SET DEFAULT PAYMENT
######################################################################

@app.route('/payments/<int:id>/default', methods=['PUT'])
def set_default(id):
    """
    Set default payment source
    This endpoint will set a payment source as the default
    """
    payment = Payment.find(id)
    if not payment:
        raise NotFound("Payment with id '{}' was not found.".format(card_id))

	others = find_by_customer_id(payment.customer_id)
	for o in others:
		o.unset_default()
		o.save()

    payment.set_default()
    payment.save()
    message = payment.serialize()
    return make_response(jsonify(message), status.HTTP_200_OK)


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    Payment.init_db(app)


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
