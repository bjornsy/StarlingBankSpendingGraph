import unittest
import requests
from unittest.mock import patch
import sys
sys.path.append(".")
from utilities import services

class TestServices(unittest.TestCase):
    #Test get_config_var()
    def test_base_url_exists(self):
        expected = 'https://api.starlingbank.com/'
        actual = services.get_config_var('api_base_url')
        self.assertEqual(expected, actual)

    #Test get_environmental_var()
    def test_get_environmental_exception_thrown(self):
        self.assertRaises(ValueError, services.get_environmental_var, 'Test')
    
    def test_personal_access_token_exists(self):
        try:
            services.get_environmental_var('StarlingPersonalAccessToken')
        except:
            self.fail('Get personal access token failed')
    
    @patch('spending_graph.services.requests.get')
    @patch('spending_graph.services.get_account_details')
    def test_get_transactions_success(self, mock_get_account_details, mock_get):
        mockAccountDetails = {'accountUid': 'accountUid', 'defaultCategory': 'categoryUid'}
        mock_get_account_details.return_value = (mockAccountDetails)

        mock_resp = requests.models.Response()
        mock_resp.status_code = 200
        mock_resp.json = lambda: {'feedItems': []}
        mock_get.return_value = mock_resp

        from_date = '2020-01-01T00:00:00.000Z'
        to_date = '2020-01-02T00:00:00.000Z'
        response = services.get_transactions(from_date, to_date)

        self.assertIsNotNone(response)
    
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
        mock_resp.status_code = 500
        mock_get.return_value = mock_resp

        from_date = '2020-01-01T00:00:00.000Z'
        to_date = '2020-01-02T00:00:00.000Z'
        
        self.assertRaises(requests.HTTPError, services.get_transactions, from_date, to_date)