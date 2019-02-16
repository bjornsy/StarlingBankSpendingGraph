import services
import pandas as pd
from matplotlib import pyplot as plt
from datetime import date

today = str(date.today())
transactions = services.get_transactions(services.get_config_var('transactions_start_date'), today)

df = pd.DataFrame(transactions)
df['created'] = pd.to_datetime(df['created'])

outbound_transactions = df[df.direction == 'OUTBOUND'][df.source != 'INTERNAL_TRANSFER'][['created', 'amount']].sort_values('created')
outbound_transactions['amount'] = abs(df['amount'])

grouped_transactions_day = outbound_transactions.groupby(pd.Grouper(key='created', freq='D')).sum()
grouped_transactions_month = outbound_transactions.groupby(pd.Grouper(key='created', freq='M')).sum()

fig, axs = plt.subplots(nrows = 1, ncols = 2)

grouped_transactions_day.plot(ax=axs[0], legend=None)
axs[0].set_title('Amount spent per day')
axs[0].set_ylim(0)
axs[0].set_xlabel('Date')
axs[0].set_ylabel('Amount spent (£)')

grouped_transactions_month.plot.bar(ax=axs[1], legend=None, rot=0)
axs[1].set_title('Amount spent per month')
axs[1].set_ylim(0)
axs[1].set_xticklabels(grouped_transactions_month.index.strftime('%Y-%b'))
axs[1].set_xlabel('Date')
axs[1].set_ylabel('Amount spent (£)')

plt.show()
