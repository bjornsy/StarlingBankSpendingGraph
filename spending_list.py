from utilities import services
import numpy as np
import matplotlib.pyplot as plt
import datetime
import pandas as pd

today = datetime.datetime.now().replace(microsecond=0).isoformat() + 'Z'
transactions = services.get_transactions(services.get_config_var('transactions_start_date'), today)

df = pd.DataFrame(transactions)
df = df[df.direction == 'OUT']
df = df[df.source != 'INTERNAL_TRANSFER']
outbound_transactions = df[['transactionTime', 'amount', 'reference', 'feedItemUid']]
outbound_transactions['amount'] = outbound_transactions['amount'].map(lambda x: x['minorUnits']/100)

outbound_transactions.to_excel("outbound_transactions.xlsx")
