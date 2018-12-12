"""
Payments Microservice API

URLs:
------
GET /payments - Returns a list of all Payments of all customers
GET /payments/{id} - Returns the Payment with a given id number
POST /payments - creates a new Payment record in database
PUT /payments/{order_id} - updates a Payment record in database
DELETE /payments/{id} - deletes a Payment record in database
PUT /payments/{id}/default - sets a Payment as default for the customer
"""


import os
import sys
import logging
import make_enum_json_serializable  # ADDED
from flask import Flask, jsonify, request, url_for, make_response, abort
from flask_api import status    # HTTP Status Codes
from flask_restplus import Api, Resource, fields
from werkzeug.exceptions import NotFound

# We use SQLAlchemy that supports SQLite, MySQL and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from models import Payment, PaymentMethodType, PaymentStatus, DataValidationError, Deault_type


# Import Flask application
from . import app


######################################################################
# Configure Swagger before initilaizing it
######################################################################
api = Api(app,
          version='1.0.0',
          title='Payment REST API Service',
          description='This is the payments server.',
          doc='/'
          # prefix='/api'
         )

# This namespace is the start of the path i.e., /payments
ns = api.namespace('payments', description='Payment operations')


# Define the model so that the docs reflect what can be sent
default_type_model = api.model('Deault_payment_type',{
        'id':fields.Integer(readOnly = True,
                            description = 'The unique id assigened internally by service'),
        'customer_id':fields.Integer(required = True,
                                    description = 'The id of the Customer'),
        'Deault_payment_type':fields.String(required = True,
                                            description = 'The Deault_payment_type of customer', enum = ["CREDIT","DEBIT","PAYPAL"])
    })
payment_model = api.model('Payment', {
    'id': fields.Integer(readOnly=True,
                         description='The unique id assigned internally by service'),
    'customer_id': fields.Integer(required=True,
                          description='The id of the Customer'),
    'order_id': fields.Integer(required=True,
                              description='The order id'),
    'payment_status': fields.String(required=True,
                            description="The payment status", enum=["UNPAID","PROCESSING","PAID"]),
    'payment_method_type': fields.String(required=True,
                            description="The payment method type", enum=["CREDIT","DEBIT","PAYPAL"]),
    'default_payment_type': fields.Boolean(required=True,
                                description='Is the payment method set as the dafault?')

})


# ######################################################################
# # Error Handlers
# ######################################################################
# @app.errorhandler(DataValidationError)
# def request_validation_error(error):
#     """ Handles Value Errors from bad data """
#     return bad_request(error)
#
# @app.errorhandler(400)
# def bad_request(error):
#     """ Handles bad reuests with 400_BAD_REQUEST """
#     message = error.message or str(error)
#     app.logger.info(message)
#     return jsonify(status=400, error='Bad Request', message=message), 400
#
# @app.errorhandler(404)
# def not_found(error):
#     """ Handles resources not found with 404_NOT_FOUND """
#     message = error.message or str(error)
#     app.logger.info(message)
#     return jsonify(status=404, error='Not Found', message=message), 404
#
# @app.errorhandler(405)
# def method_not_supported(error):
#     """ Handles unsuppoted HTTP methods with 405_METHOD_NOT_SUPPORTED """
#     message = error.message or str(error)
#     app.logger.info(message)
#     return jsonify(status=405, error='Method not Allowed', message=message), 405
#
# @app.errorhandler(415)
# def mediatype_not_supported(error):
#     """ Handles unsuppoted media requests with 415_UNSUPPORTED_MEDIA_TYPE """
#     message = error.message or str(error)
#     app.logger.info(message)
#     return jsonify(status=415, error='Unsupported media type', message=message), 415
#
# @app.errorhandler(500)
# def internal_server_error(error):
#     """ Handles unexpected server error with 500_SERVER_ERROR """
#     message = error.message or str(error)
#     app.logger.info(message)
#     return jsonify(status=500, error='Internal Server Error', message=message), 500

######################################################################
# Special Error Handlers
######################################################################
@api.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    message = error.message or str(error)
    app.logger.info(message)
    return {'status':400, 'error': 'Bad Request', 'message': message}, 400

# @api.errorhandler(DatabaseConnectionError)
# def database_connection_error(error):
#     """ Handles Database Errors from connection attempts """
#     message = error.message or str(error)
#     app.logger.critical(message)
#     return {'status':500, 'error': 'Server Error', 'message': message}, 500


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route('/healthcheck')
def healthcheck():
    """ Let them know our heart is still beating """
    return make_response(jsonify(status=200, message='Healthy'), status.HTTP_200_OK)


######################################################################
# GET INDEX
######################################################################
@app.route('/', methods=['GET'])
def index():
    """ Root URL response """
    return make_response(jsonify(name='Payments REST API Service',
                   doc=url_for('doc', _external=True)
                  ), status.HTTP_200_OK)



######################################################################
#  PATH: /pets/{id}
######################################################################
@ns.route('/<int:payment_id>')
@ns.param('payment_id', 'The Payment identifier')
class PaymentResource(Resource):
    """
    PaymentResource class

    Allows the manipulation of a single Payment
    GET /payment{id} - Returns a payment with the id
    PUT /payment{id} - Update a payment with the id
    DELETE /payment{id} -  Deletes a payment with the id
    """

    #------------------------------------------------------------------
    # RETRIEVE A PAYMENT
    #------------------------------------------------------------------
    @ns.doc('get_payments')
    @ns.response(404, 'Payment not found')
    @ns.marshal_with(payment_model)
    def get(self, payment_id):
        """
        Retrieves a single Payment for the customer
        This endpoint will return a Payment based on it's id
        """
        app.logger.info("Request to Retrieve a payment with id [%s]", payment_id)
        payment = Payment.find(payment_id)
        if not payment:
            raise NotFound("Payment with id '{}' was not found.".format(payment_id))
        return payment.serialize(), status.HTTP_200_OK

    #------------------------------------------------------------------
    # UPDATE AN EXISTING PAYMENT
    #------------------------------------------------------------------
    @ns.doc('update_payments')
    @ns.response(404, 'Payment not found')
    @ns.response(400, 'The posted Payment data was not valid')
    @ns.expect(payment_model)
    @ns.marshal_with(payment_model)
    def put(self, payment_id):
        """
        Update a Payment
        This endpoint will update a Payment resource based on the Payment Info in the body that is posted
        """
        app.logger.info('Request to Update a payment with id [%s]', payment_id)
        check_content_type('application/json')
        payment = Payment.find(payment_id)
        if not payment:
            raise NotFound('Payment with id [{}] was not found.'.format(payment_id))
        #data = request.get_json()
        data = api.payload
        app.logger.info(data)
        payment.deserialize(data)
        payment.id = payment_id
        payment.save()
        return payment.serialize(), status.HTTP_200_OK

    #------------------------------------------------------------------
    # DELETE A PAYMENT
    #------------------------------------------------------------------
    @ns.doc('delete_payments')
    @ns.response(204, 'Payment deleted')
    def delete(self, payment_id):
        """
        Delete a Payment
        This endpoint will delete a Payment based the id specified in the path
        """
        app.logger.info('Request to Delete a payment with id [%s]', payment_id)
        payment = Payment.find(payment_id)
        if payment:
            payment.delete()
        return '', status.HTTP_204_NO_CONTENT



######################################################################
#  PATH: /payments
######################################################################
@ns.route('/', strict_slashes=False)
class PaymentCollection(Resource):
    """ Handles all interactions with collections of Payments """
    #------------------------------------------------------------------
    # LIST ALL PAYMENTS
    #------------------------------------------------------------------
    @ns.doc('list_payments')
    @ns.param('category', 'List Payments by category')
    @ns.marshal_list_with(payment_model)
    def get(self):
        """ Returns all of the Payments """
        app.logger.info('Request to list Payments...')
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

        # app.logger.info('[%s] Payments returned', len(payments))
        results = [payment.serialize() for payment in payments]
        return results, status.HTTP_200_OK


    #------------------------------------------------------------------
    # ADD A NEW PAYMENT
    #------------------------------------------------------------------
    @ns.doc('create_payments')
    @ns.expect(payment_model)
    @ns.response(400, 'The posted data was not valid')
    @ns.response(201, 'Pet created successfully')
    @ns.marshal_with(payment_model, code=201)
    def post(self):
        """
        Creates a Payment
        This endpoint will create a Payment based the data in the body that is posted
        """
        app.logger.info('Request to Create a Payment')
        check_content_type('application/json')
        payment = Payment()
        app.logger.info('Payload = %s', api.payload)
        payment.deserialize(api.payload)
        payment.save()
        app.logger.info('Payment with new id [%s] saved!', payment.id)
        location_url = api.url_for(PaymentResource, payment_id=payment.id, _external=True)
        return payment.serialize(), status.HTTP_201_CREATED, {'Location': location_url}

######################################################################
# Set a payment method to default
#  PATH: /payments/{id}/default/{type}
# For Deault_payment_type table
######################################################################
@ns.route('/<int:customer_id>/default_payment_type/<string:deault_type>')
@ns.param('customer_id', 'The customer identifier')
@ns.parm("type", 'The type to be set as default type')
class dealut_payment_type_Resource(Resource):
        #------------------------------------------------------------------
    # RETRIEVE A cistomer's specific payment type
    #------------------------------------------------------------------
    @ns.doc(default_payment_type_get)
    @ns.response(404, 'Customer not found')
    @ns.marshal_with(default_type_model)
    def get(self, customer_id):
        app.logger.info("Request to Retrieve a customer default payment tyoe with customerid [%s]", customer_id)
        customer = Deault_type.find_by_customer_id(customer_id)
        if not customer:
            raise NotFound("Customer with id '{}' was not found".format(customer_id))

        return customer.serialize(), status.HTTP_200_OK

        #------------------------------------------------------------------
    # PUT A cistomer's specific payment type
    #------------------------------------------------------------------
    @ns.doc(default_payment_type_put)
    @ns.response(404, 'Customer not found')
    def put(self, cus, default_type):
        app.logger.info('Request to set a payment type as default for customer')
        customer = Deault_type.find_by_customer_id(customer_id)
        if not customer:
            return NotFound("Customer with id '{}' was not found.".format(customer_id))

        customer.dafault_payment_type = default_type
        customer.save()
        app.logger.info('The default payment method for Customer with id [%s] has been set!', customer_id)
        return customer.serialize(), status.HTTP_200_OK

    

######################################################################
# Set a payment method to default
#  PATH: /payments/{id}/default/{type}
######################################################################
@ns.route('/<int:customer_id>/default/<string:deault_type>')
@ns.param('customer_id', 'The customer identifier')
@ns.param('type', 'The type to be set as default type')
class PurchaseResource2(Resource):
    """ Purchase actions on a Payment """
    @ns.doc('purchase_payments2')
    @ns.response(404, 'Customer not found')
    @ns.response(409, 'The Customer can not change the defaut payment method')
    def put(self, customer_id, default_type):
        """
        Set default payment source
        This endpoint will set a Payment source as the default
        """
        app.logger.info('Request to set a Payment as default')
        payments = Payment.find_by_customer_id(customer)
        if not payments:
            raise NotFound("Customer with id '{}' was not found.".format(customer_id))

        for p in allpayments:
            if(p.payment_method_type == default_type)
                p.set_default()
                p.save()
            else
                p.unset_default()
                p.save()
        
        app.logger.info('The default payment method for Customer with id [%s] has been set!', customer_id)
        return payment.serialize(), status.HTTP_200_OK


######################################################################
#  PATH: /payments/{id}/default
######################################################################
@ns.route('/<int:payment_id>/default')
@ns.param('payment_id', 'The Payment identifier')
class PurchaseResource(Resource):
    """ Purchase actions on a Payment """
    @ns.doc('purchase_payments')
    @ns.response(404, 'Payment not found')
    @ns.response(409, 'The Payment is not available for purchase')
    def put(self, payment_id):
        """
        Set default payment source
        This endpoint will set a Payment source as the default
        """
        app.logger.info('Request to set a Payment as default')
        payment = Payment.find(payment_id)
        if not payment:
            raise NotFound("Payment with id '{}' was not found.".format(payment_id))

        allpayments = Payment.find_by_customer_id(payment.customer_id)
        for p in allpayments:
            p.unset_default()
            p.save()

        payment.set_default()
        payment.save()
        app.logger.info('Payment with id [%s] has been set as default!', payment.id)
        return payment.serialize(), status.HTTP_200_OK


######################################################################
#   INTERNAL SERVER ERROR
######################################################################
@app.route('/test-error')
def index1():
    raise InternalServerError("Can't Initiate Request")

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

@app.before_first_request
def init_db():
    """ Initialies the SQLAlchemy app """
    # global app
    Payment.init_db(app)


def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers['Content-Type'] == content_type:
        return
    app.logger.error('Invalid Content-Type: %s', request.headers['Content-Type'])
    abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, 'Content-Type must be {}'.format(content_type))


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
