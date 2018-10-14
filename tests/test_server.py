import unittest
import os
import json
import logging
from flask_api import status    # HTTP Status Codes
from mock import MagicMock, patch

from app.models import Card, DataValidationError, db
import app.service as service

DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')

######################################################################
#  T E S T   C A S E S
######################################################################
class TestCardServer(unittest.TestCase):
    """ Card Server Tests """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        service.app.debug = False
        service.initialize_logging(logging.INFO)
        # Set up the test database
        service.app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        """ Runs before each test """
        service.init_db()
        db.drop_all()    # clean up the last tests
        db.create_all()  # create new tables
        Card(number="123412341234", exp_month = 10, exp_year = 2019, cvc = "123",  address_zip = "10010").save()
        Card(number="567856785678", exp_month = 12, exp_year = 2022, cvc = "321",  address_zip = "07100").save()
        self.app = service.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_index(self):
        """ Test the Home Page """
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(data['name'], 'Payments REST API Service')

    def test_get_card_list(self):
        """ Get a list of Cards """
        resp = self.app.get('/cards')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)

    def test_get_card(self):
        """ Get a single Card """
        # get the id of a card
        

    def test_get_card_not_found(self):
        """ Get a Card thats not found """
        resp = self.app.get('/cards/0')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_card(self):
        """ Create a new Card """
        # save the current number of cards for later comparison
        card_count = self.get_card_count()
        # add a new card
        Card(number="567856785678", exp_month = 12, exp_year = 2022, cvc = "321",  address_zip = "07100").save()

        new_card = dict(number='333344445555', exp_month=8,exp_year=2025,cvc='789', address_zip = '10020')
        data = json.dumps(new_card)
        resp = self.app.post('/cards',
                             data=data,
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertTrue(location != None)
        # Check the data is correct
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['number'], '333344445555')
        # check that count has gone up and includes sammy
        resp = self.app.get('/cards')
        # print 'resp_data(2): ' + resp.data
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), card_count + 1)
        self.assertIn(new_json, data)

    def test_update_card(self):
        """ Update an existing Card """
        

    def test_delete_card(self):
        """ Delete a Card """
        
        # save the current number of cards for later comparrison
        

    def test_query_card_list_by_exp_year(self):
        # TO DISCUSS
        


######################################################################
# Utility functions
######################################################################

    def get_card_count(self):
        """ save the current number of cardss """
        resp = self.app.get('/cards')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        return len(data)


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
