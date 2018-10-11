"""
Models for Payments Microservice

All of the models are stored in this module

Models
------
Card - A Card used in the Service

Attributes:
-----------
number (string) - the card number, represented as a string without any separators
exp_month (integer) - the card expiration month, represented as an integer
exp_year (integer) - the card expiration year, represented as an integer
cvc (string) - the card security code, represented as an string (so that if the leading digit is 0, it is still stored correctly)
address_zip (string) - the card billing zip code, represented as a string (so that if the leading digit is 0, it is still stored correctly)
"""
import logging
from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass

class Card(db.Model):
    """
    Class that represents a Card

    This version uses a relational database for persistence which is hidden
    from us by SQLAlchemy's object relational mappings (ORM)
    """
    logger = logging.getLogger(__name__)
    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
	number = db.Column(db.String(19))
	exp_month = db.Column(db.Integer)
	exp_year = db.Column(db.Integer)
	cvc = db.Column(db.String(4))
	address_zip = db.Column(db.String(5))


    def __repr__(self):
        return '<Card %r>' % (self.name)

    def save(self):
        """
        Saves a Card to the data store
        """
        if not self.id:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        """ Removes a Card from the data store """
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Card into a dictionary """
        return {"id": self.id,
                "name": self.name,
                "category": self.category,
                "available": self.available}

    def deserialize(self, data):
        """
        Deserializes a Card from a dictionary

        Args:
            data (dict): A dictionary containing the Card data
        """
        try:
            self.number = data['number']
            self.exp_month = data['exp_month']
            self.exp_year = data['exp_year']
			self.cvc = data['cvc']
			self.address_zip = data['address_zip']
        except KeyError as error:
            raise DataValidationError('Invalid card: missing ' + error.args[0])
        except TypeError as error:
            raise DataValidationError('Invalid card: body of request contained' \
                                      'bad or no data')
        return self

    @staticmethod
    def init_db(app):
        """ Initializes the database session """
        Card.logger.info('Initializing database')
        Card.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @staticmethod
    def all():
        """ Returns all of the Cards in the database """
        Card.logger.info('Processing all Cards')
        return Card.query.all()

    @staticmethod
    def find(card_id):
        """ Finds a Card by its ID """
        Card.logger.info('Processing lookup for id %s ...', card_id)
        return Card.query.get(card_id)

    @staticmethod
    def find_or_404(card_id):
        """ Find a Card by its id """
        Card.logger.info('Processing lookup or 404 for id %s ...', card_id)
        return Card.query.get_or_404(card_id)
