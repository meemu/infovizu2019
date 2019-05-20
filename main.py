import pandas as pd

from bokeh.layouts import row, column
from bokeh.models import Select, Slider, HoverTool, Div, ColumnDataSource, Label
from bokeh.plotting import curdoc, figure




# First block of text (before the first plot)
text1 = Div(text="""<div style="margin-left: 300px; margin-bottom: 50px;">
                    <h1>World's suicides</h1>
                    <p>In the visualization below you can choose information for both of the axis and what statistic the colors and sizes of the balls are tied to. The graph’s purpose is to visualize suicide data for educational purposes and general interest. Seeing the real causality relationships between parameters that are commonly thought to affect suicide rates hopefully will help seeing the real situation. Hovering over the data points also tells which country it represents.</p>
                    <p>Data explanations: GDP for year tells what the gross domestic product. It is not really comparable between countries since smaller countries usually have a smaller GDP. That’s why there is also GDP per capita, which makes this same information comparable. Suicide amounts (suicides_no) is similar to GDP for year that it is not comparable to between countries with different populations, hence the parameter suicides/100k population.</p>
                    <p>Color is a gradient from yellow to purple, the purpler the ball is the more it has the “color” data. Size works similarly, the bigger the ball is the more it has “size” data.</p>
                    </div>
                    """, width=1380)





# Selecting the data from .csv
# downloaded from https://www.kaggle.com/russellyates88/suicide-rates-overview-1985-to-2016
df = pd.read_csv('data/master.csv')

SIZES = list(range(10, 60, 1))
COLORS = list(['#FDE724', '#B2DD2C', '#6BCD59', '#35B778', '#1E9C89', '#25828E', '#30678D', '#3E4989', '#472777', '#440154'])
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
    
    # Data to be used in the visualization
    xs = data[x.value].values
    ys = data[y.value].values
    countries = data.index.get_level_values(0).values
    
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
               tools='hover,box_zoom,save,reset',
               tooltips=[('', '@label')],
               min_border_left=100,
               min_border_bottom=100,
               min_border_right=20,
               **kw)
    p.xaxis.axis_label = x_title
    p.yaxis.axis_label = y_title
    p.grid.grid_line_color = None

    if x.value in discrete:
        p.xaxis.major_label_orientation = pd.np.pi / 4

    sz = 9
    if len(set(data[size.value])) > N_SIZES:
        groups = pd.qcut(data[size.value].values, N_SIZES, duplicates='drop')
    else:
        groups = pd.Categorical(data[size.value])
    sz = [SIZES[xx] for xx in groups.codes]

    c = "#31AADE"
    if len(set(data[color.value])) > N_COLORS:
        groups = pd.qcut(data[color.value].values, N_COLORS, duplicates='drop')
    else:
        groups = pd.Categorical(data[color.value])
    c = [COLORS[xx] for xx in groups.codes]
       
    # This datasource is used for the glyphs
    source = ColumnDataSource(
            data=dict(
                    x=xs,
                    y=ys,
                    label=countries,
                    size=sz,
                    color=c
            )
    )

    # Here we draw the circle with the provided data
    p.circle('x', 'y', size='size', color='color', line_color='white', alpha=0.7, hover_color='black', hover_alpha=0.4, source=source)

    return p


def update(attr, old, new):
    plot1.children[1] = create_figure()
    

x = Select(title='X-Axis', value='suicides/100k pop', options=continuous)
x.on_change('value', update)

y = Select(title='Y-Axis', value='gdp_for_year ($)', options=continuous)
y.on_change('value', update)

size = Select(title='Size', value='suicides/100k pop', options=continuous)
size.on_change('value', update)

color = Select(title='Color', value='gdp_for_year ($)', options=continuous)
color.on_change('value', update)

slider = Slider(start=1987, end=2015, value=2015, step=1, title='Year')
slider.on_change('value', update)





# Second block of text (after the first plot)
text2 = Div(text="""<div style="margin-left: 300px; margin-bottom: 20px;">
                    <p>There are no clear causalities using the parameters in this visualization. Comparing suicides/100k population and GDP for a year forms two vague groups and the other one seems to have some relation between a bigger GDP and more suicides. This is not clear though and the other group clearly has a small GDP throughout the different suicide amounts.</p>
                    <p>According to <a href="https://www.who.int/en/news-room/fact-sheets/detail/suicide">WHO</a> every year close to 800 000 people take their own life with many more who attempt suicide. Over 79% of global suicides occurred in low- and middle-income countries in 2016. This is affected by China and India having huge populations causing the suicide numbers to be high too.</p>
                    <p>The clearest risk factor for suicide is a previous attempt and mental disorders, like depression and alcoholism. In addition to treating mental health issues, other ways to prevent suicides are means limitation and responsible media reporting. For example restriction of access to high windows or rooves helps to reduce suicides in big cities according to <a href="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6191653/">studies</a></p>
                    </div>
                    """, width=1380)




# The second plot
# Selecting the data from .csv
# downloaded from https://www.kaggle.com/russellyates88/suicide-rates-overview-1985-to-2016
master = pd.read_csv('data/master.csv')
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
           plot_width=1400,
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
           min_border_left=300,
           min_border_top=100,
           min_border_bottom=100, 
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



# Third and last block of text (after the second plot)
text3 = Div(text="""<div style="margin-left: 300px; margin-bottom: 20px;">
                    <p>According to another <a href="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1489848/">study</a> the biggest suicide rates are in Eastern Europe, such as in Estonia, Latvia, Lithuania and to a lesser extent, Finland, Hungary and the Russian Federation. The lowest rates are found in Eastern Mediterranean region, especially in countries following Islamic traditions.</p>
                    <p>In a <a href="https://helda.helsinki.fi/bitstream/handle/10138/174896/YHDESSAL.pdf?sequence=1">study in 2009</a> they noticed that since 1940s suicide rates have been changing differently between men and women in Finland. For men a turn for the worse was between 1968-1974 and for better in 1978-1995. During the first change alcohol consumption skyrocketed and people also started moving to cities from the countryside. For women the suicide rates started to grow in 1955-1959. That’s also when women started working outside of the home. During the beginning of economic depression in 1990 and 1991 the suicides of boys aged 15-19 more than doubled in Finland according to <a href="https://yle.fi/uutiset/3-5196431">Yle</a>. They guessed it would be because of the anxiety of families and the poor financial situation. <a href"https://thl.fi/fi/web/mielenterveys/mielenterveyden-edistaminen/itsemurhien-ehkaisy">THL</a>, a Finnish counterpart to WHO, suggest the same preventative measures to suicide as WHO above.</p>
                    <p>Finland has been regarded as the happiest country in the world in several studies but we also especially historically have had relatively high suicide rates. <a href"http://healthland.time.com/2011/04/25/why-the-happiest-states-have-the-highest-suicide-rates/?xid=rss-health">Time magazine</a> suggests that “perhaps for those at the bottom end, in a way their situation may seem worse in relative terms, when compared with people who are close to them.. For someone who is quite unhappy, the relative comparison may lead to more unhappiness and depression”</p>
                    </div>
                    """, width=1380)





# Setting up the HTML layout
controls = column([x, y, color, size, slider], width=200)
plot1 = row(controls, create_figure())
layout = column(text1, plot1, text2, plot2, text3)


# Displaying everything
curdoc().add_root(layout)
curdoc().title = "HTIS59 Information Visualization 2019"