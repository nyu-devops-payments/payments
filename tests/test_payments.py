import unittest
import os
from app.models import Payment, PaymentMethodType, PaymentStatus, DataValidationError, db
from app import app

DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')
######################################################################
#  T E S T   C A S E S
######################################################################
class TestPayments(unittest.TestCase):
    """ Test Cases for Payments API """

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
        Payment.init_db(app)
        db.drop_all()    # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_create_a_payment(self):
        """ Create a payment and assert that it exists """
        payment = Payment(customer_id=12311, order_id = 11151, payment_method_type = PaymentMethodType.CREDIT, payment_status = PaymentStatus.PAID,  default_payment_type = False)
        self.assertTrue(payment != None)
        self.assertEqual(payment.id, None)
        self.assertEqual(payment.customer_id, 12311)
        self.assertEqual(payment.order_id, 11151)
        self.assertEqual(payment.payment_method_type, PaymentMethodType.CREDIT)
        self.assertEqual(payment.payment_status, PaymentStatus.PAID)
        self.assertEqual(payment.default_payment_type, False)


    def test_add_a_payment(self):
        """ Create a payment and add it to database """
        payments = Payment.all()
        self.assertEqual(payments, [])
        payment = Payment(customer_id=12011, order_id=11051, payment_method_type=PaymentMethodType.CREDIT, payment_status=PaymentStatus.PAID,  default_payment_type=True)
        self.assertTrue(payment != None)
        self.assertEqual(payment.id, None)
        payment.save()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(payment.id, 1)
        payments = Payment.all()
        self.assertEqual(len(payments), 1)


    def test_find_payment(self):
        """ Find a Payment by it's ID """
        payment11 = Payment(customer_id=12310, order_id = 13151, payment_method_type = PaymentMethodType.CREDIT, payment_status = PaymentStatus.PAID,  default_payment_type = True)
        payment11.save()
        payment = Payment.find(payment11.id)
        self.assertIsNot(payment, None)
        self.assertEqual(payment.id, payment11.id)
        self.assertEqual(payment.customer_id, 12310)
        self.assertEqual(payment.order_id, 13151)
        self.assertEqual(payment.payment_method_type, PaymentMethodType.CREDIT)
        self.assertEqual(payment.payment_status, PaymentStatus.PAID)
        self.assertEqual(payment.default_payment_type, True)


    # TODO -- Test Update Payment (Varsha)
    # def test_update_a_card(self):
    #     """ Update a Card """
    #     card = Card(number="123412341234", exp_month = 10, exp_year = 2019, cvc = "123",  address_zip = "10010", name='Gideon Popkin', balance=1500)
    #     card.save()
    #     self.assertEqual(card.id, 1)
    #     # Change it an save it
    #     card.address_zip = "10011"
    #     card.save()
    #     self.assertEqual(card.id, 1)
    #     # Fetch it back and make sure the id hasn't changed
    #     # but the data did change
    #     cards = Card.all()
    #     self.assertEqual(len(cards), 1)
    #     self.assertEqual(cards[0].address_zip, "10011")


    # TODO -- Test Delete Payment  (Shu)
    # def test_delete_a_card(self):
    #     """ Delete a Card """
    #     card = Card(number="123412341234", exp_month = 10, exp_year = 2019, cvc = "123",  address_zip = "10010", name='Fatima Mushtaq', balance=1000)
    #    	card.save()
    #     self.assertEqual(len(Card.all()), 1)
    #     # delete the card and make sure it isn't in the database
    #     card.delete()
    #     self.assertEqual(len(Card.all()), 0)


    # -- TODO Serialize a Payment Request (Varsha)
    # def test_serialize_a_card(self):
    #     """ Test serialization of a Card """
    #     card = Card(number="123412341234", exp_month = 10, exp_year = 2019, cvc = "123",  address_zip = "10010", name='Shu Tan', balance=2000)
    #     data = card.serialize()
    #     self.assertNotEqual(data, None)
    #     self.assertIn('id', data)
    #     self.assertEqual(data['id'], None)
    #     self.assertIn('number', data)
    #     self.assertEqual(data['number'], "123412341234")
    #     self.assertIn('exp_month', data)
    #     self.assertEqual(data['exp_month'], 10)
    #     self.assertIn('exp_year', data)
    #     self.assertEqual(data['exp_year'], 2019)
    #     self.assertIn('cvc', data)
    #     self.assertEqual(data['cvc'], "123")
    #     self.assertIn('address_zip', data)
    #     self.assertEqual(data['address_zip'], "10010")


    # -- TODO Deserialize a Payment Request (Shu)
    # def test_deserialize_a_card(self):
    #     """ Test deserialization of a Card """
    #     data = {"id":1,"number":"567856785678","exp_month":8,"exp_year":2010,"cvc":"321","address_zip":"10010","name":"sfvg","balance":"1000"}
    #     card = Card()
    #     card.deserialize(data)
    #     self.assertNotEqual(card, None)
    #     self.assertEqual(card.id, None)
    #     self.assertEqual(card.number, "567856785678")
    #     self.assertEqual(card.exp_month, 8)
    #     self.assertEqual(card.exp_year, 2010)
    #     self.assertEqual(card.cvc, "321")
    #     self.assertEqual(card.address_zip, "10010")
    #     self.assertEqual(card.name, "sfvg")
    #     self.assertEqual(card.balance, "1000")


    # -- TODO Deserialize a Bad Payment Data (Gideon)
    # def test_deserialize_bad_data(self):
    #     """ Test deserialization of bad data """
    #     data = "this is not a dictionary"
    #     card = Card()
    #     self.assertRaises(DataValidationError, card.deserialize, data)


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
