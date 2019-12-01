import services
import graph_helpers
import pandas as pd
from matplotlib import pyplot as plt
import datetime

today = datetime.datetime.now().replace(microsecond=0).isoformat() + 'Z'
transactions = services.get_transactions(services.get_config_var('transactions_start_date'), today)

df = pd.DataFrame(transactions)
df['transactionTime'] = pd.to_datetime(df['transactionTime'])

outbound_transactions = df[df.direction == 'OUT'][df.source != 'INTERNAL_TRANSFER'][['transactionTime', 'amount', 'counterPartyName']].sort_values('transactionTime')
outbound_transactions['amount'] = outbound_transactions['amount'].map(lambda x: x['minorUnits']/100)

grouped_transactions_day = outbound_transactions.groupby(pd.Grouper(key='transactionTime', freq='D'))
grouped_transactions_month = outbound_transactions.groupby(pd.Grouper(key='transactionTime', freq='M'))
grouped_transactions = (grouped_transactions_day, grouped_transactions_month)

grouped_transactions_day_sum = grouped_transactions_day[['transactionTime', 'amount']].sum()
grouped_transactions_month_sum = grouped_transactions_month[['transactionTime', 'amount']].sum()

fig, axs = plt.subplots(nrows = 1, ncols = 2)

grouped_transactions_day_sum.plot(ax=axs[0], legend=None, picker=True)
graph_helpers.set_common_properties(axs[0])
axs[0].set_title('Amount spent per day')

grouped_transactions_month_sum.plot.bar(ax=axs[1], legend=None, rot=0, picker=True)
graph_helpers.set_common_properties(axs[1])
axs[1].set_title('Amount spent per month')
axs[1].set_xticklabels(grouped_transactions_month_sum.index.strftime(services.get_config_var("bar_xtick_format")))

fig.canvas.mpl_connect("motion_notify_event", lambda event: graph_helpers.hover(event))
fig.canvas.mpl_connect('pick_event', lambda event: graph_helpers.pick(event, grouped_transactions))

plt.show()
