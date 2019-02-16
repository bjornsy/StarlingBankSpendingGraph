import services
import pandas as pd
from matplotlib import pyplot as plt
from datetime import date

today = str(date.today())
transactions = services.get_transactions('2018-10-01', today)

df = pd.DataFrame(transactions)
df['created'] = pd.to_datetime(df['created'])


outbound_transactions = df[df.direction == 'OUTBOUND'][['created', 'amount']].sort_values('created')
outbound_transactions['amount'] = abs(df['amount'])
grouped_transactions_day = outbound_transactions.set_index('created').groupby(pd.Grouper(freq='D')).sum()
grouped_transactions_month = outbound_transactions.set_index('created').groupby(pd.Grouper(freq='M')).sum()

#fig, axs = plt.subplots(1, 2)
grouped_transactions_day.plot()
plt.ylim(0)

grouped_transactions_month.plot.bar()

plt.show()

# plt.plot(outbound_transactions.created, outbound_transactions.amount)
# plt.show()
