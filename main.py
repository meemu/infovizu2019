import pandas as pd

from bokeh.layouts import row, column
from bokeh.models import Select, Slider
from bokeh.palettes import Spectral5
from bokeh.plotting import curdoc, figure


# Selecting the data from .csv
# downloaded from https://www.kaggle.com/russellyates88/suicide-rates-overview-1985-to-2016
df = pd.read_csv('master.csv')

SIZES = list(range(6, 22, 3))
COLORS = Spectral5
N_SIZES = len(SIZES)
N_COLORS = len(COLORS)

# unvalid data cleanup
del df['country-year']
del df['generation']
del df['HDI for year']

# Fix the broken column name and remove commas
df.rename(columns={' gdp_for_year ($) ': 'gdp_for_year ($)'},
          inplace=True)
df['gdp_for_year ($)'] = df['gdp_for_year ($)'].astype(object)
df["gdp_for_year ($)"] = df["gdp_for_year ($)"].str.replace(",","").astype(float)

# Select the variables for the visulization
columns = sorted(df.columns)
discrete = [x for x in columns if df[x].dtype == object]
continuous = [x for x in columns if x not in discrete]
continuous.remove('year')

#continuous = list(['gdp_for_year ($)', 'gdp_per_capita ($)', 'suicides_no', 'population', 'suicides/100k pop'])
#discrete = list(['year', 'age', 'country', 'sex'])

# Here we set the dataframe to sum some of the columns, and exclude some of them
summed = df.groupby(['country', 'year']).agg({'suicides_no': 'sum', 'population': 'sum', 'suicides/100k pop': 'sum', 'gdp_for_year ($)': 'min', 'gdp_per_capita ($)': 'min'})

# Initialize the view with the year 2015
data = summed.loc[(summed.index.get_level_values(1) == 2015)]

def create_figure():
    # This responds to the visualization's slider component
    data = summed.loc[(summed.index.get_level_values(1) == slider.value)]
    xs = data[x.value].values
    ys = data[y.value].values
    x_title = x.value.title()
    y_title = y.value.title()

    kw = dict()
    if x.value in discrete:
        kw['x_range'] = sorted(set(xs))
    if y.value in discrete:
        kw['y_range'] = sorted(set(ys))
    kw['title'] = "%s vs %s" % (x_title, y_title)

    p = figure(plot_height=900, plot_width=1200, tools='save', **kw)
    p.xaxis.axis_label = x_title
    p.yaxis.axis_label = y_title

    if x.value in discrete:
        p.xaxis.major_label_orientation = pd.np.pi / 4

    sz = 9
    if size.value != 'None':
        if len(set(data[size.value])) > N_SIZES:
            groups = pd.qcut(data[size.value].values, N_SIZES, duplicates='drop')
        else:
            groups = pd.Categorical(data[size.value])
        sz = [SIZES[xx] for xx in groups.codes]

    c = "#31AADE"
    if color.value != 'None':
        if len(set(data[color.value])) > N_COLORS:
            groups = pd.qcut(data[color.value].values, N_COLORS, duplicates='drop')
        else:
            groups = pd.Categorical(data[color.value])
        c = [COLORS[xx] for xx in groups.codes]

    p.circle(x=xs, y=ys, color=c, size=sz, line_color="white", alpha=0.6, hover_color='white', hover_alpha=0.5)

    return p


def update(attr, old, new):
    layout.children[1] = create_figure()


x = Select(title='X-Axis', value='suicides/100k pop', options=continuous)
x.on_change('value', update)

y = Select(title='Y-Axis', value='gdp_for_year ($)', options=continuous)
y.on_change('value', update)

size = Select(title='Size', value='None', options=['None'] + continuous)
size.on_change('value', update)

color = Select(title='Color', value='None', options=['None'] + continuous)
color.on_change('value', update)

slider = Slider(start=1987, end=2015, value=2015, step=1, title='Year')
slider.on_change('value', update)

controls = column([x, y, color, size], width=200)
layout = row(controls, create_figure(), slider)

curdoc().add_root(layout)
curdoc().title = "Suicides"