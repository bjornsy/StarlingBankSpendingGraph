def set_common_properties(axs_reference: 'matplotlib.axes._subplots.AxesSubplot') -> None:
    axs_reference.set_ylim(0)
    axs_reference.set_xlabel('Date')
    axs_reference.set_ylabel('Amount spent (£)')

def create_annot(axs_reference: 'matplotlib.axes._subplots.AxesSubplot') -> 'matplotlib.text.Annotation':
    annot = axs_reference.annotate("", xy=(0,0), xytext=(-20,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)
    return annot

def format_currency(num: float) -> str:
    return '£{:.2f}'.format(num)
