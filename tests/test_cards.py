import unittest
import os
from app.models import Card, DataValidationError, db
from app import app

######################################################################
#  T E S T   C A S E S
######################################################################
class TestcCards(unittest.TestCase):
    """ Test Cases for Cards """

    @classmethod
    def setUpClass(cls):
        """ These run once per Test suite """
        app.debug = False
        # Set up the test database
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        Card.init_db(app)
        db.drop_all()    # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_create_a_card(self):
        """ Create a card and assert that it exists """
        card = Card(number="123412341234", exp_month = 10, exp_year = 2019, cvc = "123",  address_zip = "10010")
        self.assertTrue(card != None)
        self.assertEqual(card.id, None)
        self.assertEqual(card.number, "123412341234")
        self.assertEqual(card.exp_month, 10)
        self.assertEqual(card.exp_year, 2019)
        self.assertEqual(card.cvc, "123")
        self.assertEqual(card.address_zip, "10010")


    def test_add_a_card(self):
        """ Create a card and add it to the database """
        cards = Card.all()
        self.assertEqual(cards, [])
        card = Card(number="123412341234", exp_month = 10, exp_year = 2019, cvc = "123",  address_zip = "10010")
        self.assertTrue(card != None)
        self.assertEqual(card.id, None)
        card.save()
        # Asert that it was assigned an id and shows up in the database
        self.assertEqual(card.id, 1)
        cards = Card.all()
        self.assertEqual(len(cards), 1)

    def test_update_a_card(self):
        """ Update a Card """
        card = Card(number="123412341234", exp_month = 10, exp_year = 2019, cvc = "123",  address_zip = "10010")
        card.save()
        self.assertEqual(card.id, 1)
        # Change it an save it
        card.address_zip = "10011"
        card.save()
        self.assertEqual(card.id, 1)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        cards = Card.all()
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0].address_zip, "10011")

    def test_delete_a_card(self):
        """ Delete a Card """
        card = Card(number="123412341234", exp_month = 10, exp_year = 2019, cvc = "123",  address_zip = "10010")
       	card.save()
        self.assertEqual(len(Card.all()), 1)
        # delete the card and make sure it isn't in the database
        card.delete()
        self.assertEqual(len(Card.all()), 0)

    def test_serialize_a_card(self):
        """ Test serialization of a Card """
        card = Card(number="123412341234", exp_month = 10, exp_year = 2019, cvc = "123",  address_zip = "10010")
        data = card.serialize()
        self.assertNotEqual(data, None)
        self.assertIn('id', data)
        self.assertEqual(data['id'], None)
        self.assertIn('number', data)
        self.assertEqual(data['number'], "123412341234")
        self.assertIn('exp_month', data)
        self.assertEqual(data['exp_month'], 10)
        self.assertIn('exp_year', data)
        self.assertEqual(data['exp_year'], 2019)
        self.assertIn('cvc', data)
        self.assertEqual(data['cvc'], "123")
        self.assertIn('address_zip', data)
        self.assertEqual(data['address_zip'], "10010")

    def test_deserialize_a_card(self):
        """ Test deserialization of a Card """
        data = {"id":1,"number":"567856785678","exp_month":8,"exp_year":2010,"cvc":"321","address_zip":"10010"}
        card = Card()
        card.deserialize(data)
        self.assertNotEqual(card, None)
        self.assertEqual(card.id, None)
        self.assertEqual(card.number, "567856785678")
        self.assertEqual(card.exp_month, 8)
        self.assertEqual(card.exp_year, 2010)
        self.assertEqual(card.cvc, "321")
        self.assertEqual(card.address_zip, "10010")

    def test_deserialize_bad_data(self):
        """ Test deserialization of bad data """
        data = "this is not a dictionary"
        card = Card()
        self.assertRaises(DataValidationError, card.deserialize, data)

    def test_find_card(self):
        """ Find a Card by ID """
        Card(number="123412341234", exp_month = 10, exp_year = 2019, cvc = "123",  address_zip = "10010").save()
        card5678 = Card(number="567856785678", exp_month = 12, exp_year = 2022, cvc = "321",  address_zip = "07110")
        card5678.save()
        card = Card.find(card5678.id)
        self.assertIsNot(card, None)
        self.assertEqual(card.id, card5678.id)
        self.assertEqual(card.number, "567856785678")
        self.assertEqual(card.exp_month, 12)
        self.assertEqual(card.exp_year, 2022)
        self.assertEqual(card.cvc, "321")
        self.assertEqual(card.address_zip, "07110")




######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
