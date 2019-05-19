import pandas as pd

from bokeh.layouts import row, column
from bokeh.models import Select, Slider, HoverTool, Div, ColumnDataSource
from bokeh.plotting import curdoc, figure




# First block of text (before the first plot)
text1 = Div(text="""Your <a href="https://en.wikipedia.org/wiki/HTML">HTML</a>-supported text is initialized with the <b>text</b> argument.  The
remaining div arguments are <b>width</b> and <b>height</b>. For this example, those values
are <i>200</i> and <i>100</i> respectively.""",
width=1000, height=100)





# Selecting the data from .csv
# downloaded from https://www.kaggle.com/russellyates88/suicide-rates-overview-1985-to-2016
df = pd.read_csv('master.csv')

SIZES = list(range(10, 50, 10))
COLORS = list(['#FDE724', '#79D151', '#22A784', '#29788E', '#404387', '#440154'])
N_SIZES = len(SIZES)
N_COLORS = len(COLORS)

# unvalid data cleanup
del df['country-year']
del df['generation']
del df['HDI for year']

# Fix the broken column name and remove commas
df.rename(columns={' gdp_for_year ($) ': 'gdp_for_year ($)'},
          inplace=True)
df["gdp_for_year ($)"] = df["gdp_for_year ($)"].str.replace(",","").astype(float)

# Select the variables for the visulization
columns = sorted(df.columns)
discrete = [x for x in columns if df[x].dtype == object]
continuous = [x for x in columns if x not in discrete]
continuous.remove('year')

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

    p = figure(plot_height=900,
               plot_width=1200,
               tools='save,box_zoom,reset',
               min_border_left=100,
               min_border_bottom=100,
               min_border_right=20,
               **kw)
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
    plot1.children[1] = create_figure()
    

x = Select(title='X-Axis', value='suicides/100k pop', options=continuous)
x.on_change('value', update)

y = Select(title='Y-Axis', value='gdp_for_year ($)', options=continuous)
y.on_change('value', update)

size = Select(title='Size', value='suicides/100k pop', options=['None'] + continuous)
size.on_change('value', update)

color = Select(title='Color', value='gdp_for_year ($)', options=['None'] + continuous)
color.on_change('value', update)

slider = Slider(start=1987, end=2015, value=2015, step=1, title='Year')
slider.on_change('value', update)





# Second block of text (after the first plot)
text2 = Div(text="""Your <a href="https://en.wikipedia.org/wiki/HTML">HTML</a>-supported text is initialized with the <b>text</b> argument.  The
remaining div arguments are <b>width</b> and <b>height</b>. For this example, those values
are <i>200</i> and <i>100</i> respectively.""",
width=1000, height=50)




# The second plot
# Selecting the data from .csv
# downloaded from https://www.kaggle.com/russellyates88/suicide-rates-overview-1985-to-2016
master = pd.read_csv('master.csv')
columns2 = master[['country','year','sex','suicides_no']]
finland = columns2[columns2['country'] == 'Finland']

# Males by year
males = finland[finland['sex'] == 'male']
males_yearly = males.groupby('year').sum()
males_ds = ColumnDataSource(males_yearly)

# Females by year
females = finland[finland['sex'] == 'female']
females_yearly = females.groupby('year').sum()
females_ds = ColumnDataSource(females_yearly)

plot2 = figure(plot_height=500,
           plot_width=1200,
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
           tools='save',
           min_border_left=100,
           min_border_top=100,
           min_border_bottom=20, 
           min_border_right=20)

plot2.grid.grid_line_color = None

plot2.line(source=males_ds, x='year', y='suicides_no', color='#22A784',
       line_width=2.5, legend='Males')

plot2.line(source=females_ds, x='year', y='suicides_no', color='#404387',
       line_width=2, legend='Females')

plot2.add_tools(HoverTool(
    tooltips=[
        ( 'Year', '@year' ),
        ( 'Suicides', '@suicides_no' )
    ],

    mode='vline'
))



# Setting up the HTML layout
controls = column([x, y, color, size, slider], width=200)
plot1 = row(create_figure(), controls)
layout = column(text1, plot1, text2, plot2)


# Displaying everything
curdoc().add_root(layout)
curdoc().title = "Suicides"