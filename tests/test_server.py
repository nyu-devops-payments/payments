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

        Card(number="123412341234", exp_month = 10, exp_year = 2019, cvc = "123",  address_zip = "10010", name="nick1", balance= 200.5).save()
        Card(number="567856785678", exp_month = 12, exp_year = 2022, cvc = "321",  address_zip = "07100", name="Fatima M", balance= 3000).save()
        Card(number="345634563456", exp_month = 9, exp_year = 2020, cvc = "323",  address_zip = "07100", name="Varsha Murali", balance= 2000).save()
        Card(number="345634563456", exp_month = 11, exp_year = 2021, cvc = "311",  address_zip = "07110", name="Gedeon Popkin", balance= 500).save()

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
        self.assertEqual(len(data), 4)

    def test_get_card(self):
        """ Get a single Card """
        # get the id of a card
        resp = self.app.get('/cards/2')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        card = Card.find_by_number('123412341234')[0]
        resp = self.app.get('/cards/{}'.format(card.id),
                            content_type='application/json')
       
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(data['name'], card.name)



    def test_get_card_not_found(self):
        """ Get a Card thats not found """
        resp = self.app.get('/cards/0')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


    def test_get_card_by_name(self):
        """ Get Card by Card Holder Name """
        # get the id of a card
        resp = self.app.get('/cards', query_string='name=Fatima M')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


    def test_create_card(self):
        """ Create a new Card """
        # save the current number of cards for later comparison
        card_count = self.get_card_count()
        # add a new card
        #Card(number="567856785678", exp_month = 12, exp_year = 2022, cvc = "321",  address_zip = "07100").save()

        new_card = dict(number='333344445555', exp_month=8, exp_year=2025, cvc='789', address_zip='10020', name='xyzba', balance=50)
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
        card = Card.find_by_number("123412341234")[0];
        new_card5678 = dict(number="123412341234", exp_month = 12, exp_year = 2020, cvc = "321",  address_zip = "07111", name='xyzba', balance=50)
        data = json.dumps(new_card5678)
        resp = self.app.put('/cards/{}'.format(card.id),
                            data=data,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['exp_year'], 2020)
        self.assertEqual(new_json['address_zip'], '07111')

    def test_update_card_not_found(self):
        """ Update an existing Card """
        card = Card.find_by_number("123412341234")[0];
        new_card5678 = dict(number="123412341234", exp_month = 12, exp_year = 2020, cvc = "321",  address_zip = "07111", name='xyzba', balance=50)
        data = json.dumps(new_card5678)
        resp = self.app.put('/cards/{}'.format(0),
                            data=data,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        



    def test_delete_card(self):
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

    def test_query_card_list_by_name(self):

        """ Query Cards by exp_year """
        resp = self.app.get('/cards',
                            query_string='name=nick1')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreater(len(resp.data), 0)
        self.assertIn('123412341234', resp.data)
        data = json.loads(resp.data)
        query_item = data[0]
        self.assertEqual(query_item['exp_year'], 2019)

    def test_query_card_list_by_number(self):

        """ Query Cards by exp_year """
        resp = self.app.get('/cards',
                            query_string='number=123412341234')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreater(len(resp.data), 0)
        self.assertIn('123412341234', resp.data)
        data = json.loads(resp.data)
        query_item = data[0]
        self.assertEqual(query_item['exp_year'], 2019)

    def test_charge_card_not_found(self):
        
        resp = self.app.put('/cards/{}'.format(100)+'/{}'.format(20.5))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_charge_card(self):
        card = Card.find_by_number('567856785678')[0];
        resp = self.app.put('/cards/{}'.format(card.id)+'/{}'.format(20.5))
        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)

    def test_charge_card_not_acceptable(self):
        card = Card.find_by_number('567856785678')[0];
        resp = self.app.put('/cards/{}'.format(card.id)+'/{}'.format(3320.5))
        self.assertEqual(resp.status_code, status.HTTP_406_NOT_ACCEPTABLE)


######################################################################
# Utility functions
######################################################################

    def get_card_count(self):
        """ save the current number of cards """
        resp = self.app.get('/cards')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        return len(data)

######################################################################
# Patch Mock Tests
######################################################################

    @patch('app.service.Card.find_by_name')
    def test_bad_request(self, bad_request_mock):
        """ Test a Bad Request error from Find By Name """
        bad_request_mock.side_effect = DataValidationError()
        resp = self.app.get('/cards', query_string='name=xyz')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('app.service.Card.find_by_name')
    def test_mock_search_data(self, card_find_mock):
        """ Test showing how to mock data """
        card_find_mock.return_value = [MagicMock(serialize=lambda: {'name': 'xyz'})]
        resp = self.app.get('/cards', query_string='name=xyz')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # @patch('app.service.Card.deserialize')
    # def test_mock_deserialize_data(self, bad_request_mock):
    #     """ Test a Bad Request - Deserialization Error """
    #     bad_request_mock.side_effect = DataValidationError()
    #     resp = self.app.get('/cards', query_string='number=null')
    #     self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_method_not_allowed(self):
        resp = self.app.put('/cards')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
