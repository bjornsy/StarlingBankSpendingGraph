import os
import requests
import json

with open('config.json') as config_file:
    config = json.load(config_file)

def get_config_var(name: str) -> str:
    '''Returns config variables from config.json
    Args:
        name (str): Name of variable to get
    Returns:
        Corresponding variable
    '''
    return config[name]


def get_environmental_var(name: str) -> str:
    '''Returns environmental variables for keys/secrets
    Args:
        name (str): Name of environmental variable to get
    Returns:
        Corresponding variable
    Raises:
        ValueError: if variable with name not found
    '''
    variable = os.environ.get(name)
    if not variable:
        raise ValueError('Environmental variable not found')
    else:
        return variable

token = get_environmental_var('StarlingPersonalAccessToken')
headers = {'Authorization': f'Bearer {token}'}

def get_account_details() -> dict:
    '''Gets accountUid and categoryUid for further API calls
    Returns: Dict of account details
    '''
    endpoint = config['api_base_url'] + config['accounts_url']
    response = requests.get(endpoint, headers=headers)
    if response.ok:
        return response.json()['accounts'][0]
    else:
        response.raise_for_status()
    
def get_transactions(from_date=None, to_date=None) -> object:
    '''Gets all transactions spent for a given timeframe
    Args:
        from_date (str): YYYY-MM-DD
        to_date (str): YYYY-MM-DD
    Returns:
        list of transactions
    '''
    account_details = get_account_details()
    accountUid = account_details['accountUid']
    categoryUid = account_details['defaultCategory']
    endpoint = config['api_base_url'] + config['transactions_url'].replace('{accountUid}', accountUid).replace('{categoryUid}', categoryUid)
    query_string = f'?minTransactionTimestamp={from_date}&maxTransactionTimestamp={to_date}' if from_date or to_date else ''
    response = requests.get(endpoint + query_string, headers=headers)
    if response.ok:
        return extract_transactions(response)
    else:
        response.raise_for_status()

def extract_transactions(response_object) -> list:
    transactions = response_object.json()['feedItems']
    return transactions

