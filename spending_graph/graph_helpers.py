def set_common_properties(axs_reference: 'matplotlib.axes._subplots.AxesSubplot') -> None:
    axs_reference.set_ylim(0)
    axs_reference.set_xlabel('Date')
    axs_reference.set_ylabel('Amount spent (£)')
