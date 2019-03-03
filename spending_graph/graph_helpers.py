def set_common_properties(subplot: 'matplotlib.axes._subplots.AxesSubplot') -> None:
    subplot.set_ylim(0)
    subplot.set_xlabel('Date')
    subplot.set_ylabel('Amount spent (£)')
    annot = subplot.annotate("", xy=(0,0), xytext=(-20,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

def update_annot(ind, annot, line) -> None:
    horizontal_pos_array = ind["ind"] #Where the hover event takes place (normalised horizontal position)
    x,y = line.get_data()
    annot.xy = (x[horizontal_pos_array[0]], y[horizontal_pos_array[0]]) #Using minimum value for consistency (if hovering over more than one)
    amount_text = format_currency(y[horizontal_pos_array.min()])
    date_text = x[horizontal_pos_array.min()]
    text = f'{date_text}, {amount_text}'
    annot.set_text(text)
    annot.get_bbox_patch().set_alpha(0.4)

def update_annot_bar(artist, annot_bar) -> None:
    center_x = artist.get_x() + artist.get_width() / 2
    center_y = artist.get_y() + artist.get_height() / 2
    annot_bar.xy = (center_x, center_y)
    text = format_currency(artist.get_height())
    annot_bar.set_text(text)
    annot_bar.get_bbox_patch().set_alpha(0.4)

def hover(event) -> None:
    if event.inaxes:   
        subplot = event.inaxes 
        if subplot.lines:
            fig = subplot.figure
            line = subplot.lines[0]
            annot = subplot.texts[0]
            cont, ind = line.contains(event)
            if cont:
                update_annot(ind, annot, line)
                annot.set_visible(True)
                fig.canvas.draw_idle()
            else:
                vis = annot.get_visible()
                if vis:
                    annot.set_visible(False)
                    fig.canvas.draw_idle()
        if subplot.containers:
            an_artist_is_hovered = False
            fig = subplot.figure
            annot_bar = subplot.texts[0]
            containers = subplot.containers[0]
            for artist in containers:
                contains, _ = artist.contains(event)
                if contains:
                    an_artist_is_hovered = True
                    update_annot_bar(artist, annot_bar)
                    annot_bar.set_visible(True)
                    fig.canvas.draw_idle()
            if not an_artist_is_hovered:
                annot_bar.set_visible(False)
                fig.canvas.draw_idle()

def pick(event) -> None:
    return None

def format_currency(num: float) -> str:
    return '£{:.2f}'.format(num)
