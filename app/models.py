"""
Models for Payments Microservice


All of the models are stored in this module

Models
------
Payment - A Payment Method used in the Service for making a payment


Attributes:
-----------


"""
import os
import json
import logging
from . import db
from enum import Enum
from app.custom_exceptions import DataValidationError


class PaymentStatus(Enum):
   UNPAID = 1
   PROCESSING = 2
   PAID = 3


class PaymentMethodType(Enum):
   __order__ ='CREDIT DEBIT PAYPAL'
   CREDIT = 1
   DEBIT = 2
   PAYPAL = 3

class Payment(db.Model):
    """
    Class that represents a Payment

    This version uses a relational database for persistence which is hidden
    from us by SQLAlchemy's object relational mappings (ORM)
    """
    logger = logging.getLogger(__name__)
    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    order_id = db.Column(db.Integer, nullable=False)
    payment_status = db.Column(db.Enum(PaymentStatus))
    payment_method_type = db.Column(db.Enum(PaymentMethodType), nullable=False)
    default_payment_type = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Payment %r>' % (self.name)

    def save(self):
        """
        Saves a Payment to the data store
        """
        if not self.id:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        """ Removes a Payment from the data store """
        db.session.delete(self)
        db.session.commit()

    def set_default(self):
        """ Sets a Payment as the default """
        self.default_payment_type = True

    def unset_default(self):
        """ Disables the default status for a Payment """
        self.default_payment_type = False

    def serialize(self):
        """ Serializes a Payment into a dictionary """
        return {"id": self.id,
                "customer_id": self.customer_id,
                "order_id": self.order_id,
                "payment_status": self.payment_status,
		        "payment_method_type": self.payment_method_type,
		        "default_payment_type": self.default_payment_type,
	           }


    def deserialize(self, data):
        """
        Deserializes a Payment from dictionary

        Args:
            data (dict): A dictionary containing the Payment Data
        """
        try:
            self.customer_id = data['customer_id']
            self.order_id = data['order_id']
            self.payment_status = data['payment_status']
            self.payment_method_type = data['payment_method_type']
            self.default_payment_type = data['default_payment_type']

        except KeyError as error:
            raise DataValidationError('Invalid Payment Data: missing ' + error.args[0])
        except TypeError as error:
            raise DataValidationError('Invalid Payment Data: body of request contained' \
                                      'bad or no data')
        return self


    @staticmethod
    def init_db():
        """ Initializes the database session """
        Payment.logger.info('Initializing database')
        db.create_all()  # make our sqlalchemy tables

    @staticmethod
    def remove_all():
        """ Removes all Payments from the database """
        Payment.query.delete()
        # db.drop_all()    # clean up the last tests
        # db.create_all()  # create new tables

    @staticmethod
    def all():
        """ Returns all of the Payments in the database """
        Payment.logger.info('Processing all Payments')
        return Payment.query.all()


    @staticmethod
    def find(id):
        """ Finds a Payment by its ID """
        Payment.logger.info('Processing lookup for payment_id %s ...', id)
        return Payment.query.get(id)


    @staticmethod
    def find_or_404(payment_id):
        """ Find a Payment by its id """
        Payment.logger.info('Processing lookup or 404 for payment_id %s ...', payment_id)
        return Payment.query.get_or_404(payment_id)


    @staticmethod
    def find_by_customer_id(customer_id):
        """ Returns all Payments for the given customer_id
        Args:
            customer_id (int): the customer_id of the Customer you want to match
        """
        Payment.logger.info('Processing payments query for %s ...', customer_id)
        return Payment.query.filter(Payment.customer_id == customer_id).all()


    @staticmethod
    def find_by_order_id(order_id):
        """ Returns Payments for the given order_id
        Args:
            order_id (int): the number of the order_id you want to match
        """
        Payment.logger.info('Processing order_id query for %s ...', order_id)
        return Payment.query.filter(Payment.order_id == order_id)


    @staticmethod
    def find_by_payment_status(payment_status):
        """ Returns all of the Payments with the given payment status
        Args:
            payment_status (enum): the payment_status of Payments you want to match
        """
        Payment.logger.info('Processing payment_status query for %s ...', payment_status)
        return Payment.query.filter(Payment.payment_status == payment_status).all()


    @staticmethod
    def find_by_payment_method_type(payment_method_type):
        """ Returns all Payments with the given payment method type
        Args:
            payment_method_type (int): the payment_status of Payments you want to match
        """
        Payment.logger.info('Processing payment_method_type query for %s ...', payment_method_type)
        return Payment.query.filter(Payment.payment_method_type == payment_method_type).all()


    @staticmethod
    def get_default_payment_type():
        """ Returns the default payment method type
        Args:
        default_payment_type(): of all Payments which is set to true
        """
        Payment.logger.info('Processing default_payment_type query for %s ...', default_payment_type)
        return Payment.query.filter(Payment.default_payment_type.is_(True)).all()
