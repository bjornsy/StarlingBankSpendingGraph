import unittest
from unittest.mock import patch
from spending_graph import services

class TestServices(unittest.TestCase):
    #Test get_config_var()
    def test_base_url_exists(self):
        expected = 'https://api.starlingbank.com'
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
    
    def test_get_transactions(self):
        with patch('spending_graph.services.requests.get') as mock_get:
            mock_get.return_value.ok = True
            response = services.get_transactions()
            self.assertIsNotNone(response)

            mock_get.return_value.ok = False
            response = services.get_transactions()
            self.assertIsNone(response)