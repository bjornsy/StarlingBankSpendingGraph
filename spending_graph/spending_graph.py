import services
import graph_helpers
import pandas as pd
from matplotlib import pyplot as plt
import datetime

#TODO:
#Add button to switch between graphs, clear up labels
#Add total spend in one year

def get_transactions() -> list:
    today = datetime.datetime.now().replace(microsecond=0).isoformat() + 'Z'
    transactions = services.get_transactions(services.get_config_var('transactions_start_date'), today)
    return transactions

def get_outbound_transactions(transactions: list) -> pd.DataFrame:
    df = pd.DataFrame(transactions)
    df['transactionTime'] = pd.to_datetime(df['transactionTime'])

    df = df[df.direction == 'OUT']
    df = df[df.source != 'INTERNAL_TRANSFER']
    df = df[~df.feedItemUid.isin(services.get_config_var('feed_items_to_ignore'))]
    outbound_transactions = df[['transactionTime', 'amount', 'counterPartyName']].sort_values('transactionTime')
    outbound_transactions['amount'] = outbound_transactions['amount'].map(lambda x: x['minorUnits']/100)

    return outbound_transactions

def get_grouped_transactions_day(outbound_transactions: pd.DataFrame) -> pd.core.groupby.generic.DataFrameGroupBy:
    grouped_transactions_day = outbound_transactions.groupby(pd.Grouper(key='transactionTime', freq='D'))
    return grouped_transactions_day

def get_grouped_transactions_month(outbound_transactions: pd.DataFrame) -> pd.core.groupby.generic.DataFrameGroupBy:
    grouped_transactions_month = outbound_transactions.groupby(pd.Grouper(key='transactionTime', freq='M'))
    return grouped_transactions_month

def get_grouped_transactions_day_sum(grouped_transactions_day: pd.core.groupby.generic.DataFrameGroupBy) -> pd.DataFrame:
    grouped_transactions_day_sum = grouped_transactions_day[['transactionTime', 'amount']].sum()
    return grouped_transactions_day_sum

def get_grouped_transactions_month_sum(grouped_transactions_month: pd.core.groupby.generic.DataFrameGroupBy) -> pd.DataFrame:
    grouped_transactions_month_sum = grouped_transactions_month[['transactionTime', 'amount']].sum()
    return grouped_transactions_month_sum
    
def plot_day_sum(grouped_transactions_day_sum: pd.DataFrame, axs) -> None:
    grouped_transactions_day_sum.plot(ax=axs[0], legend=None, picker=True)
    graph_helpers.set_common_properties(axs[0])
    axs[0].set_title('Amount spent per day')

def plot_month_sum(grouped_transactions_month_sum: pd.DataFrame, axs) -> None:
    grouped_transactions_month_sum.plot.bar(ax=axs[1], legend=None, rot=0, picker=True)
    graph_helpers.set_common_properties(axs[1])
    axs[1].set_title('Amount spent per month')
    axs[1].set_xticklabels(grouped_transactions_month_sum.index.strftime(services.get_config_var("bar_xtick_format")))

def set_figure(fig, grouped_transactions_day_and_month: tuple) -> None:
    fig.canvas.mpl_connect("motion_notify_event", lambda event: graph_helpers.hover(event))
    fig.canvas.mpl_connect('pick_event', lambda event: graph_helpers.pick(event, grouped_transactions_day_and_month))

def plot_graphs(grouped_transactions_day_sum, grouped_transactions_month_sum, grouped_transactions_day_and_month: tuple) -> None:
    fig, axs = plt.subplots(nrows = 1, ncols = 2)
    plot_day_sum(grouped_transactions_day_sum, axs)
    plot_month_sum(grouped_transactions_month_sum, axs)
    set_figure(fig, grouped_transactions_day_and_month)
    plt.show()

def main():
    transactions = get_transactions()
    outbound_transactions = get_outbound_transactions(transactions)
    grouped_transactions_day = get_grouped_transactions_day(outbound_transactions)
    grouped_transactions_month = get_grouped_transactions_month(outbound_transactions)
    grouped_transactions_day_and_month = (grouped_transactions_day, grouped_transactions_month)
    grouped_transactions_day_sum = get_grouped_transactions_day_sum(grouped_transactions_day)
    grouped_transactions_month_sum = get_grouped_transactions_month_sum(grouped_transactions_month)
    plot_graphs(grouped_transactions_day_sum, grouped_transactions_month_sum, grouped_transactions_day_and_month)

if __name__ == "__main__":
    main()