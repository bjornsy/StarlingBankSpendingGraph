import unittest
import requests
from unittest.mock import patch
import sys
sys.path.append(".")
from utilities import services

class TestServices(unittest.TestCase):
      
    @patch('os.environ.get')
    def test_personal_access_token_exists(self, mock_environ_get):
        mock_token = 'token'
        mock_environ_get.return_value = mock_token

        token = services.get_environmental_var('TokenName')

        mock_environ_get.assert_called_once
        self.assertEqual(token, mock_token)

    @patch('os.environ.get')
    def test_personal_access_token_raises(self, mock_environ_get):
        mock_environ_get.return_value = None
        
        self.assertRaises(ValueError, services.get_environmental_var, 'TokenName')

    @patch('spending_graph.services.requests.get')
    def test_get_account_details(self, mock_get):
        mock_account_details = {"accountUid":"accountUid","defaultCategory":"defaultCategory","currency":"GBP","createdAt":"2018-04-01T12:32:56.967Z"}
        mock_resp = requests.models.Response()
        mock_resp.status_code = 200
        mock_resp.json = lambda: {"accounts":[mock_account_details]}
        mock_get.return_value = mock_resp

        response = services.get_account_details()

        mock_get.assert_called_once()
        self.assertEqual(response, mock_account_details)

    @patch('spending_graph.services.requests.get')
    def test_get_account_details_raises(self, mock_get):
        mock_resp = requests.models.Response()
        mock_resp.status_code = 400
        mock_get.return_value = mock_resp

        self.assertRaises(requests.HTTPError, services.get_account_details)

    @patch('spending_graph.services.requests.get')
    @patch('spending_graph.services.get_account_details')
    def test_get_transactions_success(self, mock_get_account_details, mock_get):
        mock_transactions = [{
            'feedItemUid':'feedItemUid',
            'categoryUid':'categoryUid',
            'amount':{'currency': 'GBP', 'minorUnits': 1160},
            'sourceAmount':{'currency': 'GBP', 'minorUnits': 1160},
            'direction':'OUT',
            'updatedAt':'2020-04-25T17:08:19.717Z',
            'transactionTime':'2020-04-25T17:08:19.615Z',
            'source':'MASTER_CARD',
            'sourceSubType':'CONTACTLESS',
            'status':'PENDING',
            'transactingApplicationUserUid':'Uid',
            'counterPartyType':'MERCHANT',
            'counterPartyUid':'Uid',
            'counterPartyName':'Restaurant name',
            'counterPartySubEntityUid':'Uid',
            'reference':'Restaurant',
            'country':'GB',
            'spendingCategory':'EATING_OUT',
            'roundUp':{'amount': {'currency': 'GBP', 'minorUnits': 40}, 'goalCategoryUid': 'Uid'}
        }]
        mockAccountDetails = {'accountUid': 'accountUid', 'defaultCategory': 'categoryUid'}
        mock_get_account_details.return_value = (mockAccountDetails)

        mock_resp = requests.models.Response()
        mock_resp.status_code = 200
        mock_resp.json = lambda: {'feedItems': mock_transactions}
        mock_get.return_value = mock_resp

        from_date = '2020-01-01T00:00:00.000Z'
        to_date = '2020-01-02T00:00:00.000Z'
        response = services.get_transactions(from_date, to_date)

        mock_get_account_details.assert_called_once()
        mock_get.assert_called_once()
        self.assertEqual(response, mock_transactions)
    
    def test_get_transactions_no_args_raises(self):
        from_date = None
        to_date = None

        self.assertRaises(ValueError, services.get_transactions, from_date, to_date)
    
    @patch('spending_graph.services.requests.get')
    @patch('spending_graph.services.get_account_details')
    def test_get_transactions_api_raises(self, mock_get_account_details, mock_get):
        mockAccountDetails = {'accountUid': 'accountUid', 'defaultCategory': 'categoryUid'}
        mock_get_account_details.return_value = (mockAccountDetails)

        mock_resp = requests.models.Response()
        mock_resp.status_code = 400
        mock_get.return_value = mock_resp

        from_date = '2020-01-01T00:00:00.000Z'
        to_date = '2020-01-02T00:00:00.000Z'

        self.assertRaises(requests.HTTPError, services.get_transactions, from_date, to_date)