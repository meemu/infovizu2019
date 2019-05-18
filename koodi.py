import pandas as pd

from bokeh.io import show, output_file
from bokeh.plotting import figure, curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, HoverTool, Div, Select
from bokeh.sampledata.autompg import autompg_clean as df
from bokeh.palettes import Inferno



# Selecting the data from .csv
# downloaded from https://www.kaggle.com/russellyates88/suicide-rates-overview-1985-to-2016
master = pd.read_csv('master.csv')
columns = master[['country','year','sex','suicides_no']]
finland = columns[columns['country'] == 'Finland']

# Males by year
males = finland[finland['sex'] == 'male']
males_yearly = males.groupby('year').sum()
males_ds = ColumnDataSource(males_yearly)

# Females by year
females = finland[finland['sex'] == 'female']
females_yearly = females.groupby('year').sum()
females_ds = ColumnDataSource(females_yearly)

p = figure(plot_height=500,
           plot_width=1000,
           h_symmetry=True,
           x_axis_label='Year',
           x_axis_type='linear',
           x_axis_location='below',
           x_range=(1987, 2015),
           y_axis_label='Number of suicides',
           y_axis_type='linear',
           y_axis_location='left',
           y_range=(0, 1300),
           title='Suicide Rates in Finland from 1987 to 2016',
           title_location='above',
           toolbar_location='below',
           tools='save',
           min_border_left=100,
           min_border_top=50,
           min_border_right=20)

p.grid.grid_line_color = None

p.line(source=males_ds, x='year', y='suicides_no', color='darkcyan',
       line_width=2.5, legend='Males')

p.line(source=females_ds, x='year', y='suicides_no', color='deeppink',
       line_width=2, legend='Females')

p.add_tools(HoverTool(
    tooltips=[
        ( 'Year', '@year' ),
        ( 'Suicides', '@suicides_no' )
    ],

    mode='vline'
))

text1 = Div(text="""Your <a href="https://en.wikipedia.org/wiki/HTML">HTML</a>-supported text is initialized with the <b>text</b> argument.  The
remaining div arguments are <b>width</b> and <b>height</b>. For this example, those values
are <i>200</i> and <i>100</i> respectively.""",
width=1000, height=50)

text2 = Div(text="""Your <a href="https://en.wikipedia.org/wiki/HTML">HTML</a>-supported text is initialized with the <b>text</b> argument.  The
remaining div arguments are <b>width</b> and <b>height</b>. For this example, those values
are <i>200</i> and <i>100</i> respectively.""",
width=1000, height=100)

output_file('index.html')
