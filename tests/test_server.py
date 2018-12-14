import unittest
import os
import json
import logging
from flask_api import status    # HTTP Status Codes
from mock import MagicMock, patch

from app.models import Payment, PaymentMethodType, PaymentStatus, db
import app.service as service
from app.custom_exceptions import DataValidationError as DataValidationError
from app import error_handlers as error_handlers

DATABASE_URI = os.getenv('DATABASE_URI', None)

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_405_METHOD_NOT_ALLOWED = 405
HTTP_409_CONFLICT = 409
#DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')

######################################################################
#  T E S T   C A S E S
######################################################################
class TestPaymentServer(unittest.TestCase):
    """ Payment Server Tests """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        service.app.debug = False
        service.initialize_logging(logging.INFO)
        # Set up the test database
        if DATABASE_URI:
            service.app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

    @classmethod
    def tearDownClass(cls):
        pass

    def test_index(self):
        """ Test the Home Page """
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        #self.assertTrue('Payments REST API Service' in resp.data)


    def setUp(self):
        self.app = service.app.test_client()
        service.initialize_logging(logging.CRITICAL)
        service.init_db()
        service.data_reset()
        Payment(customer_id=12302, order_id = 11150, payment_method_type = "CREDIT", payment_status = "PAID",  default_payment_type = False).save()
        Payment(customer_id=12302, order_id = 12143, payment_method_type = "DEBIT",  payment_status = "PAID",  default_payment_type = False).save()
        Payment(customer_id=14121, order_id = 11122, payment_method_type = "CREDIT", payment_status = "PAID",  default_payment_type = False).save()
        Payment(customer_id=14121, order_id = 15189, payment_method_type = "PAYPAL", payment_status = "PROCESSING",  default_payment_type = False).save()


    def test_get_payments_list(self):
        """ Get a list of all Payments """
        resp = self.app.get('/payments')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(len(data), 4)


    def test_get_payment_by_order_id(self):
        """ Get Payment by Order Id """
        # get the id of a payment
        resp = self.app.get('/payments', query_string='order_id=15189')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


    def test_create_payment(self):
        """ Creates a new Payment """
        # save the current number of payments for later comparison
        all_payments_count = self.get_all_payments_count()
        # add a new payment method
        new_payment = dict(customer_id=53121, order_id=15190, payment_method_type=PaymentMethodType.DEBIT, payment_status=PaymentStatus.PAID,  default_payment_type=False)

        data = json.dumps(new_payment)
        resp = self.app.post('/payments',
                             data=data,
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertTrue(location != None)

        # Check the data is correct
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['order_id'], 15190)

        # check that count has gone up and includes the new payment resource
        resp = self.app.get('/payments')
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), all_payments_count + 1)
        self.assertIn(new_json, data)


    def test_query_payment_list_by_customer_id(self):
        """ Query Payments by customer_id """
        resp = self.app.get('/payments',
                            query_string='customer_id=12302')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreater(len(resp.data), 0)
        self.assertIn('12302', resp.data)
        self.assertNotIn('11111', resp.data)
        data = json.loads(resp.data)
        query_item = data[0]
        self.assertEqual(query_item['customer_id'], 12302)


    def test_query_payment_list_by_order_id(self):
        """ Query Payments by order_id """
        resp = self.app.get('/payments',
                            query_string='order_id=12143')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreater(len(resp.data), 0)
        self.assertIn('12302', resp.data)
        data = json.loads(resp.data)
        query_item = data[0]
        self.assertEqual(query_item['order_id'], 12143)


    def test_query_payment_list_by_payment_status(self):
        """ Query Payments by payment_status """
        resp = self.app.get('/payments',
                            query_string='payment_status=PAID')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreater(len(resp.data), 0)
        self.assertIn('PAID', resp.data)
        data = json.loads(resp.data)
        query_item = data[0]
        self.assertEqual(query_item['payment_status'], 'PaymentStatus.PAID')


    def test_query_payment_list_by_payment_method_type(self):
        """ Query Payments by payment_method_type """
        resp = self.app.get('/payments', query_string='payment_method_type=CREDIT')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreater(len(resp.data), 0)
        self.assertIn('CREDIT', resp.data)
        data = json.loads(resp.data)
        query_item = data[0]
        self.assertEqual(query_item['payment_method_type'], 'PaymentMethodType.CREDIT')


    def test_get_payment(self):
        """ Get a single Payment """
        # get id of the payment
        resp = self.app.get('/payments/2')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        payment = Payment.find_by_order_id('11122')[0]
        resp = self.app.get('/payments/{}'.format(payment.id),
                            content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(data['customer_id'], payment.customer_id)


    def test_get_payment_not_found(self):
        """ Get a Payment thats not found """
        resp = self.app.get('/payments/0')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


    def test_set_default(self):
        """ Set the default payment for a customer """
        # Get a payment and confirm default is false
        payment = Payment.find_by_order_id(11150)[0]
        self.assertEqual(payment.default_payment_type, False)

        # Get second payment for the customer and confirm default is false
        payment2 = Payment.find_by_order_id(12143)[0]
        self.assertEqual(payment2.default_payment_type, False)

        # Sanity check - make sure we're testing two records of the same customer
        self.assertEqual(payment.customer_id, payment2.customer_id)

        # Set default
        resp = self.app.put('/payments/{}/default'.format(payment.id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Confirm first is true
        payment = Payment.find_by_order_id(11150)[0]
        temp1 = Payment.find_by_order_id(payment.order_id)[0]
        self.assertEqual(temp1.default_payment_type, True)

        # Confirm second is still false
        payment2 = Payment.find_by_order_id(12143)[0]
        temp2 = Payment.find_by_order_id(payment2.order_id)[0]
        self.assertEqual(temp2.default_payment_type, False)

        # Now swap - set the second to default
        resp2 = self.app.put('/payments/{}/default'.format(payment2.id))
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)

        # Confirm first is false
        payment = Payment.find_by_order_id(11150)[0]
        temp3 = Payment.find(payment.id)
        self.assertEqual(temp3.default_payment_type, False)

        # Confirm second is true
        payment2 = Payment.find_by_order_id(12143)[0]
        temp4 = Payment.find(payment2.id)
        self.assertEqual(temp4.default_payment_type, True)


    def test_set_default_not_found(self):
        """ Sets a default payment with an invalid ID """
        resp = self.app.put('/payments/0/default')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


    def test_update_payment(self):
        """ Update an existing Payment Resource """

        payment = Payment.find_by_order_id('15189')[0];

        test_payment = dict(customer_id=14121, order_id = 15189, payment_method_type = PaymentMethodType.PAYPAL, payment_status = PaymentStatus.PAID,  default_payment_type = False)
        data = json.dumps(test_payment)

        resp = self.app.put('/payments/{}'.format(payment.id),
                            data=data,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['payment_status'], 'PaymentStatus.PAID')
        self.assertEqual(new_json['payment_method_type'], 'PaymentMethodType.PAYPAL')


    def test_update_payment_not_found(self):
        """ Update an existing Payment Resource not in DB"""
        payment = Payment.find_by_order_id('15189')[0];
        test_payment = dict(customer_id=14121, order_id = 15189, payment_method_type = "PAYPAL", payment_status = "PROCESSING",  default_payment_type = False)
        data = json.dumps(test_payment)
        resp = self.app.put('/payments/0',
                            data=data,
                            content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


    def test_delete_payment(self):
        """ Delete a Payment """
        payment = Payment.find_by_order_id(15189)[0];
        # save the current number of cards for later comparrison
        payments_count = self.get_all_payments_count()
        resp = self.app.delete('/payments/{}'.format(payment.id),
                               content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        new_count = self.get_all_payments_count()
        self.assertEqual(new_count, payments_count - 1)

    def test_payments_reset(self):
        resp = self.app.delete("/payments/reset")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_health(self):
        """ Test the server health checker """
        resp = self.app.get('/health')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(data['name'], 'Payments REST API Service - Health')
        self.assertEqual(data['status'], 'OK')
        self.assertEqual(data['url'].split('/')[3], 'health')

######################################################################
# Utility functions
######################################################################
    def get_all_payments_count(self):
        """ get the current number of total payments from data store """
        resp = self.app.get('/payments')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        return len(data)

######################################################################
# Patch Mock Tests
######################################################################

    @patch('app.service.Payment.find_by_customer_id')
    def test_bad_request(self, bad_request_mock):
        """ Test a Bad Request error from Find By Customer Id """
        bad_request_mock.side_effect = DataValidationError()
        resp = self.app.get('/payments', query_string='customer_id=111x50')
        #self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('app.service.Payment.find_by_order_id')
    def test_mock_search_data(self, payment_find_mock):
        """ Test showing how to mock data """
        payment_find_mock.return_value = [MagicMock(serialize=lambda: {'order_id': '01'})]
        resp = self.app.get('/payments', query_string='order_id=01')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


    def test_method_not_allowed(self):
        resp = self.app.put('/payments')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    def test_check_content_type(self):
        new_payment = dict(customer_id=53121, order_id=15190, payment_method_type=PaymentMethodType.DEBIT, payment_status=PaymentStatus.PAID,  default_payment_type=False)
        data = json.dumps(new_payment)
        resp = self.app.post('/payments',
                             data=data,
                             content_type='application/json1')
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        # Make sure it is an invalid content Type
        contentTyp = resp.headers.get('Content-Type', None)
        print(contentTyp)
        self.assertTrue(contentTyp != None)
        
        
    def test_create_bad_payment(self):
        """ Creates a new bad Payment Request """
        # save the current number of payments for later comparison
        all_payments_count = self.get_all_payments_count()
        # add a new payment method
        new_payment = dict(customer_id="", order_id="", payment_method_type="", payment_status="",  default_payment_type="")
        data = json.dumps(new_payment)
        resp = self.app.post('/payments',
                             data=data,
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


    def test_update_payment_bad_request(self):
        """ Update an existing Payment Resource """

        payment = Payment.find_by_order_id('15189')[0];
        test_payment = dict(customer_id="", order_id = "", payment_method_type = "", payment_status = "",  default_payment_type = "")
        data = json.dumps(test_payment)
        resp = self.app.put('/payments/{}'.format(payment.id),
                               data=data,
                               content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        
    
    #
    # def test_internal_server_error(self):
    #     """ Test an Internal Server error """
    #     resp = self.app.get('/test-error')
    #     self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    #
    #
    # def test_bad_request_error(self):
    #     """ Test an Request Valid error """
    #     resp = self.app.get('/test-bad-request-error')
    #     self.assertEqual(resp, status.HTTP_500_INTERNAL_SERVER_ERROR)
    #
    #
    # def test_not_found_error(self):
    #     """ Test an Request Valid error """
    #     resp = self.app.get('/test-not-found-error')
    #     self.assertEqual(resp, status.HTTP_500_INTERNAL_SERVER_ERROR)
    #
    #
    # def test_method_not_supported_error(self):
    #     """ Test an Method Not supported error """
    #     resp = self.app.get('/test-method-not-supported-error')
    #     self.assertEqual(resp, status.HTTP_500_INTERNAL_SERVER_ERROR)
    #
    #
    # def test_media_type_not_supported_error(self):
    #     """ Test Media Type Not supported error """
    #     resp = self.app.get('/test-media-type-not-supported-error')
    #     self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
    #


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
