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
        Card(number="567856785678", exp_month = 12, exp_year = 2022, cvc = "321",  address_zip = "07100",name = 'nick2', balance = 300.0).save()
        Card(number="345634563456", exp_month = 9, exp_year = 2020, cvc = "323",  address_zip = "07100").save()

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
        self.assertEqual(len(data), 3)

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
        #Card(number="567856785678", exp_month = 12, exp_year = 2022, cvc = "321",  address_zip = "07100").save()

        new_card = dict(number='333344445555', exp_month=8,exp_year=2025,cvc='789', address_zip = '10020', name = 'nick', balance = 50.0)
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

        card = Card.find_by_number("567856785678")[0];
        new_card5678 = dict(number="567856785678", exp_month = 12, exp_year = 2020, cvc = "321",  address_zip = "07111",name = 'nnick', balance = 1000.0) 
        data = json.dumps(new_card5678)
        resp = self.app.put('/cards/{}'.format(card.id),
                            data=data,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['exp_year'], 2020)
        self.assertEqual(new_json['address_zip'], '07111')
        self.assertEqual(new_json['name'], 'nnick')
        self.assertEqual(new_json['balance'], 1000.0)
        

    def test_delete_card(self):
        """ Delete a Card """
        """ Delete a Card """
        card = Card.find_by_number("123412341234")[0];
        # save the current number of cards for later comparrison
        card_count = self.get_card_count()
        resp = self.app.delete('/cards/{}'.format(card.id),
                               content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        new_count = self.get_card_count()
        self.assertEqual(new_count, card_count - 1)
        
        # save the current number of cards for later comparrison
        

    def test_query_card_list_by_exp_year(self):
        # TO DISCUSS

        card = Card.find_by_number("123412341234")[0];
        # save the current number of cards for later comparrison
        card_count = self.get_card_count()
        resp = self.app.delete('/cards/{}'.format(card.id),
                               content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        new_count = self.get_card_count()
        self.assertEqual(new_count, card_count - 1)
        

    def test_query_card_list_by_exp_year(self):
        """ Query Cards by exp_year """
        resp = self.app.get('/cards',
                            query_string='exp_year=2020')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreater(len(resp.data), 0)
        self.assertIn('345634563456', resp.data)
        self.assertNotIn('123412341234', resp.data)
        data = json.loads(resp.data)
        query_item = data[0]
        self.assertEqual(query_item['exp_year'], 2020)

        


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
