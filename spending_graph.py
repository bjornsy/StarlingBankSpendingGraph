from utilities import services
from utilities import graph_helpers
import pandas as pd
from matplotlib import pyplot as plt
import datetime
from datetime import timezone

#TODO:
#Add button to switch between graphs or split into 2 separate
#Add total numbers on graph

items_to_ignore = services.get_config_var('feed_items_to_ignore')
items_to_divide = services.get_config_var('feed_items_to_divide')

def get_transactions() -> list:
    today = datetime.datetime.now().replace(microsecond=0).isoformat() + 'Z'
    transactions = services.get_transactions(services.get_config_var('transactions_start_date'), today)
    return transactions

def get_outbound_transactions(transactions: list) -> pd.DataFrame:
    df = pd.DataFrame(transactions)
    df['transactionTime'] = pd.to_datetime(df['transactionTime'])

    df = df[df.direction == 'OUT']
    df = df[df.source != 'INTERNAL_TRANSFER']
    df = df[~df.feedItemUid.isin(items_to_ignore)]
    df['amount'] = df.apply(lambda x: calculate_amount(x.amount, x.feedItemUid), axis=1)
    outbound_transactions = df[['transactionTime', 'amount', 'counterPartyName']].sort_values('transactionTime')

    return outbound_transactions

def calculate_amount(amount: object, feedItemUid: str) -> float:
    final_amount = amount['minorUnits']/100
    if feedItemUid in items_to_divide:
        return final_amount/items_to_divide[feedItemUid]
    return final_amount

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

def calculate_total_spend_past_year(outbound_transactions) -> float:
    one_year_ago = (datetime.datetime.now() - datetime.timedelta(days=365)).replace(tzinfo=timezone.utc)
    total = outbound_transactions[(outbound_transactions['transactionTime'] > one_year_ago)][['amount']].sum()['amount']
    return total

def calculate_total_spend_since_jan(outbound_transactions) -> float:
    first_of_year = (datetime.datetime(datetime.datetime.now().year, 1, 1)).replace(tzinfo=timezone.utc)
    total = outbound_transactions[(outbound_transactions['transactionTime'] > first_of_year)][['amount']].sum()['amount']
    return total

def plot_day_sum(grouped_transactions_day_sum: pd.DataFrame, axs, totals) -> None:
    grouped_transactions_day_sum.plot(ax=axs[0], legend=None, picker=True)
    graph_helpers.set_common_properties(axs[0])
    axs[0].set_title(f'Amount spent per day ({graph_helpers.format_currency(totals[0])} past year, {graph_helpers.format_currency(totals[1])} since Jan)')

def plot_month_sum(grouped_transactions_month_sum: pd.DataFrame, axs) -> None:
    grouped_transactions_month_sum.plot.bar(ax=axs[1], legend=None, rot=0, picker=True)
    graph_helpers.set_common_properties(axs[1])
    axs[1].set_title('Amount spent per month')
    axs[1].set_xticklabels(grouped_transactions_month_sum.index.strftime(services.get_config_var("bar_xtick_format")))

def set_figure(fig, grouped_transactions_day_and_month: tuple) -> None:
    fig.canvas.mpl_connect("motion_notify_event", lambda event: graph_helpers.hover(event))
    fig.canvas.mpl_connect('pick_event', lambda event: graph_helpers.pick(event, grouped_transactions_day_and_month))

def plot_graphs(grouped_transactions_day_sum, grouped_transactions_month_sum, grouped_transactions_day_and_month: tuple, totals: tuple) -> None:
    fig, axs = plt.subplots(nrows = 1, ncols = 2)
    plot_day_sum(grouped_transactions_day_sum, axs, totals)
    plot_month_sum(grouped_transactions_month_sum, axs)
    set_figure(fig, grouped_transactions_day_and_month)
    plt.subplots_adjust(bottom=0.15)
    plt.xticks(rotation='vertical')
    plt.show()

def main():
    transactions = get_transactions()
    outbound_transactions = get_outbound_transactions(transactions)
    totals_past_year = (calculate_total_spend_past_year(outbound_transactions), calculate_total_spend_since_jan(outbound_transactions)) 
    grouped_transactions_day = get_grouped_transactions_day(outbound_transactions)
    grouped_transactions_month = get_grouped_transactions_month(outbound_transactions)
    grouped_transactions_day_and_month = (grouped_transactions_day, grouped_transactions_month)
    grouped_transactions_day_sum = get_grouped_transactions_day_sum(grouped_transactions_day)
    grouped_transactions_month_sum = get_grouped_transactions_month_sum(grouped_transactions_month)
    plot_graphs(grouped_transactions_day_sum, grouped_transactions_month_sum, grouped_transactions_day_and_month, totals_past_year)

if __name__ == "__main__":
    main()