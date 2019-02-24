import services
import graph_helpers
import pandas as pd
from matplotlib import pyplot as plt
from datetime import date

today = str(date.today())
transactions = services.extract_transactions(services.get_transactions(services.get_config_var('transactions_start_date'), today))

df = pd.DataFrame(transactions)
df['created'] = pd.to_datetime(df['created'])

outbound_transactions = df[df.direction == 'OUTBOUND'][df.source != 'INTERNAL_TRANSFER'][['created', 'amount']].sort_values('created')
outbound_transactions['amount'] = abs(df['amount'])

grouped_transactions_day = outbound_transactions.groupby(pd.Grouper(key='created', freq='D')).sum()
grouped_transactions_month = outbound_transactions.groupby(pd.Grouper(key='created', freq='M')).sum()

fig, axs = plt.subplots(nrows = 1, ncols = 2)

plot_day = grouped_transactions_day.plot(ax=axs[0], legend=None)
line = plot_day.lines[0]
graph_helpers.set_common_properties(axs[0])
axs[0].set_title('Amount spent per day')

grouped_transactions_month.plot.bar(ax=axs[1], legend=None, rot=0)
graph_helpers.set_common_properties(axs[1])
axs[1].set_title('Amount spent per month')
axs[1].set_xticklabels(grouped_transactions_month.index.strftime('%Y-%b'))




annot = axs[0].annotate("", xy=(0,0), xytext=(-20,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
annot.set_visible(False)

def update_annot(ind):
    horizontal_pos_array = ind["ind"] #Where the hover event takes place (normalised horizontal position)
    x,y = line.get_data()
    annot.xy = (x[horizontal_pos_array[0]], y[horizontal_pos_array[0]]) #Using minimum value for consistency (if hovering over more than one)
    amount_text = graph_helpers.format_currency(y[horizontal_pos_array.min()])
    date_text = x[horizontal_pos_array.min()]
    text = f'{date_text}, £{amount_text}'
    annot.set_text(text)
    annot.get_bbox_patch().set_alpha(0.4)

def hover(event):
    vis = annot.get_visible()
    if event.inaxes == axs[0]:
        cont, ind = line.contains(event)
        if cont:
            update_annot(ind)
            annot.set_visible(True)
            fig.canvas.draw_idle()
        else:
            if vis:
                annot.set_visible(False)
                fig.canvas.draw_idle()

fig.canvas.mpl_connect("motion_notify_event", hover)

plt.show()
