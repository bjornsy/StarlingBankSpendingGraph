import unittest
import requests
from unittest.mock import patch
import pandas as pd
import datetime
from datetime import timezone
import sys
sys.path.append(".")
import spending_graph

class TestSpendingGraph(unittest.TestCase):

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
        },
        {
            'feedItemUid':'feedItemUid2',
            'categoryUid':'categoryUid2',
            'amount':{'currency': 'GBP', 'minorUnits': 2000},
            'direction':'IN', #INBOUND
            'transactionTime':'2020-04-25T17:08:19.615Z',
            'source':'MASTER_CARD',
            'counterPartyName':'Restaurant name', 
        },
        {
            'feedItemUid':'feedItemUid3',
            'categoryUid':'categoryUid3',
            'amount':{'currency': 'GBP', 'minorUnits': 800},
            'direction':'OUT',
            'transactionTime':'2020-04-25T17:08:19.615Z',
            'source':'INTERNAL_TRANSFER', #INTERNAL_TRANSFER
            'counterPartyName':'Restaurant name', 
        },
        {
            'feedItemUid':'ignoreUid', #TO BE IGNORED
            'categoryUid':'categoryUid4',
            'amount':{'currency': 'GBP', 'minorUnits': 90},
            'direction':'OUT',
            'transactionTime':'2020-04-25T17:08:19.615Z',
            'source':'MASTER_CARD',
            'counterPartyName':'Restaurant name', 
        },
        {
            'feedItemUid':'divideUid', #TO BE DIVIDED
            'categoryUid':'categoryUid5',
            'amount':{'currency': 'GBP', 'minorUnits': 1000},
            'direction':'OUT',
            'transactionTime':'2020-03-25T17:08:19.615Z',
            'source':'MASTER_CARD',
            'counterPartyName':'Restaurant name', 
        }]

    @patch('spending_graph.services.get_transactions')
    def test_get_transactions(self, mock_get_transactions):
        mock_get_transactions.return_value = self.mock_transactions

        transactions = spending_graph.get_transactions()

        mock_get_transactions.assert_called_once()
        self.assertEqual(transactions, self.mock_transactions)

    @patch('spending_graph.items_to_divide', {'divideUid': 2})
    @patch('spending_graph.items_to_ignore', ['ignoreUid'])
    def test_get_outbound_transactions(self):
        outbound_transactions = spending_graph.get_outbound_transactions(self.mock_transactions)

        self.assertEqual(len(outbound_transactions), 2) #Only outbound and non-ignored transactions
        self.assertEqual(outbound_transactions.columns.values.tolist(), ['transactionTime', 'amount', 'counterPartyName'])
        self.assertEqual(outbound_transactions['amount'].iloc[1], 11.60) #Amount divided by 100
        self.assertEqual(outbound_transactions['amount'].iloc[0], 5.00) #Amount divided by 100 and by 2
        self.assertLess(outbound_transactions['transactionTime'].iloc[0], outbound_transactions['transactionTime'].iloc[1]) #Sorted by time, oldest first

    @patch('spending_graph.items_to_divide', {'divideUid': 2})
    @patch('spending_graph.items_to_ignore', ['ignoreUid'])
    def test_calculate_total_spend_all(self):
        all_date_from = datetime.datetime(2020, 1, 1).replace(tzinfo=timezone.utc)
        outbound_transactions = spending_graph.get_outbound_transactions(self.mock_transactions)

        total = spending_graph.calculate_total_spend(outbound_transactions, all_date_from)

        self.assertEqual(total, outbound_transactions['amount'].iloc[0] + outbound_transactions['amount'].iloc[1])
    
    @patch('spending_graph.items_to_divide', {'divideUid': 2})
    @patch('spending_graph.items_to_ignore', ['ignoreUid'])
    def test_calculate_total_spend_one(self):
        one_date_from = datetime.datetime(2020, 4, 1).replace(tzinfo=timezone.utc)
        outbound_transactions = spending_graph.get_outbound_transactions(self.mock_transactions)

        total = spending_graph.calculate_total_spend(outbound_transactions, one_date_from)

        self.assertEqual(total, outbound_transactions['amount'].iloc[1])