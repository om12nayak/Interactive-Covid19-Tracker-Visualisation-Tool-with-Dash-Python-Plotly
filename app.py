""" By Om Prasad Nayak - https://www.linkedin.com/in/om-prasad-nayak-315226150/
for our team AIProbably - https://www.youtube.com/channel/UCVRIJ7lXBgzM61n3dRAgxHw/videos"""

# -*- coding: utf-8 -*-
# Importing statements for dash
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
from plotly.graph_objs import *
from dash.dependencies import Input, Output

# Importing other packages
from datetime import datetime, timedelta
import json
import pandas as pd
import numpy as np
import re
import requests

# Adding stylesheets
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Initialising Dash app and adding the stylesheets to our app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# Here the title we can set for the webpage
app.title = 'Covid Reason ?'

# Layout(CSS) for the dash table.
layout_table = dict(
    autosize=True,
    height=510,
    font=dict(color="#191A1A"),
    titlefont=dict(color="#191A1A", size='14'),
    margin=dict(
        l=35,
        r=35,
        b=35,
        t=45
    ),
    hovermode="closest",
    plot_bgcolor='#fffcfc',
    paper_bgcolor='#fffcfc',
    legend=dict(font=dict(size=10), orientation='h'),
    border='thin lightgrey solid',
    max_height=510,
    font_size=12,
    margin_top=20
)

# Saving the first server time when refreshed
current_server_startime = datetime.now()

# Loading the covid19 data from https://github.com/pomber/covid19 which I have stored in a JSON file
# json.load() function helps in loading the file into a json, arg is the filehandler
with open('data_pomber.json', 'r') as filehandle:
    data1 = json.load(filehandle)

# Taking the backup of data so that even we mesh up our original data, we have a backup.
# And if you normally assign to another dictionary then any changes to the original, will affect the backup also.
# So here we are storing it with dict(), this way it wont affect the original.
data_backup = dict(data1)

# Initialising a dataframe with the data that we have loaded from the json file.
df = pd.DataFrame(data_backup)

# Reading the excel file and storing it in a dataframe. Gapminder(https://www.gapminder.org/data/)
population = pd.read_excel('population_total.xlsx')

# Taking only the country and 2020 year from the dataset.
population_2020 = population[['country', 2020]]

# Storing the country names from the json file
country_available = data1.keys()

# Here we are taking a common set of countries for which we have data like some countries dont have the covid19 data and
# similarly for some countries we dont have the population data. So trying to make an intersection but basically giving
# more focus on the Covid19 data.
# The same below thing can be done using intersection() of set but for clarity I have used this method.
country_population_minus = list(
    set(country_available) - (set(country_available) - set(list(population_2020['country']))))

# Sorting the list as after set manipulation it becomes unordered.
country_population_minus.sort()

# Defining a dataFrame for our use which will be only on the filtered countries.
df_country_popu_minus = pd.DataFrame()

# Initialising the above by iterating on the filtered countries.
# enumerate() gives us the index and the value respectively.
# loc() helps us to assign and get the value at a particular index, it takes row label and column label respectively,
# here we are using loc() to assign value
# We are creating 6 columns
for lab, value in enumerate(country_population_minus):
    df_country_popu_minus.loc[lab, "country"] = value
    # data1[country_name] gives a list, from that we are taking the last element(by -ve indexing) which is the latest date
    df_country_popu_minus.loc[lab, "confirmed"] = data1[value][-1]['confirmed']
    # population_2020.loc[population_2020['country'] == value] gives us a dataframe where the country is same as value,
    # from that we are taking the 2020 column, which again gives us a series(explicitly typecasting it to list so that
    # we can do indexing) list which has only one element, so we are using the 0th element
    df_country_popu_minus.loc[lab, "population"] = \
        list((population_2020.loc[population_2020['country'] == value])[2020])[0]
    df_country_popu_minus.loc[lab, "recovered"] = data1[value][-1]['recovered']
    df_country_popu_minus.loc[lab, "death"] = data1[value][-1]['deaths']
    df_country_popu_minus.loc[lab, "active"] = data1[value][-1]['confirmed'] - data1[value][-1]['deaths'] - \
                                               data1[value][-1]['recovered']

# Setting the row index of the dataframe same as the country column, which was previously number starting from 0.
# We could have actually did the same thing in the loop itself by setting the first argument of loc() as value
# instead of lab
df_country_popu_minus.index = country_population_minus

# Starting of the layout of the app for the frontend
app.layout = html.Div(
    html.Div(
        [
            html.Div(
                [
                    html.H1(
                        children='!=Corona Virus Tracker',
                        className='nine columns'
                    ),
                    html.Img(
                        src="https://firebasestorage.googleapis.com/v0/b/images-54a5a.appspot.com/o/COVID%2019.png?alt"
                            "=media&token=e6b48990-339e-4d85-bb36-4bf9460c7bf6",
                        className='three columns',
                        style={
                            'height': '8%',
                            'width': '8%',
                            'float': 'right',
                            'position': 'relative',
                            'padding-top': 0,
                            'padding-right': 0
                        },
                    ),
                    html.H4(
                        children='''Dash Tutorial On Covid19''',
                        className='nine columns'
                    ),
                    html.Button(
                        'Refresh Data', id='submit-val', n_clicks=0, n_clicks_timestamp=-1,
                        className='three columns',
                        style={
                            'float': 'right'}
                    ),
                    html.P(id='placeholder',
                           style={
                               'float': 'right',
                               'display': 'none'
                           }
                    )

                ], className="row"
            ),
            html.Div(
                html.H3(
                    children='WORLD STATS',
                    className='twelve columns',
                    style={
                        'padding-top': 10,
                        'padding-right': 0,
                        'text-align': 'center'
                    },
                ),
                className="row"
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.P('Confirmed'),
                            html.P(df_country_popu_minus['confirmed'].sum())
                        ],
                        className='three columns',
                        style={
                            'text-align': 'center'
                        }
                    ),
                    html.Div(
                        [
                            html.P('Active'),
                            html.P(df_country_popu_minus['active'].sum())
                        ],
                        className='three columns',
                        style={
                            'text-align': 'center'
                        }
                    ),
                    html.Div(
                        [
                            html.P('Recovered'),
                            html.P(df_country_popu_minus['recovered'].sum())
                        ],
                        className='three columns',
                        style={
                            'text-align': 'center'
                        }
                    ),
                    html.Div(
                        [
                            html.P('Deaths'),
                            html.P(df_country_popu_minus['death'].sum())
                        ],
                        className='three columns',
                        style={
                            'text-align': 'center'
                        }
                    ),
                ], className="row",
                style={
                    'padding-top': 4,
                    'border': 'thin lightgrey solid'
                }
            ),
            html.Div(
                [
                    html.P(
                        children='Select Countries to see in the Table (MULTIPLE) :',
                        className='twelve columns',
                        style={
                            'margin-top': 20,
                        }
                    ),
                ], className="row"),
            html.Div(
                [
                    html.Div(
                        [
                            dcc.Dropdown(
                                id='choose_multi_country_dropdown',
                                options=[{"label": i, "value": i} for i in (["All"] + country_population_minus)],
                                value=['All'],
                                multi=True,
                                style={'position': 'relative', 'zIndex': '999'},
                                placeholder="Select Country"
                            )
                        ], className="twelve columns")
                ], className='row',
                style=
                {
                    'margin-top': 4
                }
            ),
            html.Div(
                [
                    html.Div(
                        [
                            dt.DataTable(
                                data=df_country_popu_minus.to_dict('records'),
                                columns=[{"name": i.capitalize(), "id": i} for i in df_country_popu_minus.columns],
                                id='datatable',
                                style_header=
                                {
                                    'fontWeight': 'bold',
                                    'border': 'thin lightgrey solid',
                                    'backgroundColor': 'rgb(100, 100, 100)',
                                    'color': 'white'
                                },
                                style_cell={
                                    'fontFamily': 'Open Sans',
                                    'textAlign': 'left',
                                    'width': '150px',
                                    'minWidth': '180px',
                                    'maxWidth': '180px',
                                    'whiteSpace': 'no-wrap',
                                    'overflow': 'hidden',
                                    'textOverflow': 'ellipsis',
                                    'backgroundColor': 'Rgb(230,230,250)'
                                },
                                style_data_conditional=[
                                    {
                                        'if': {'row_index': 'odd'},
                                        'backgroundColor': 'rgb(248, 248, 248)'
                                    },
                                    {
                                        'if': {'column_id': 'country'},
                                        'backgroundColor': 'rgb(255, 255, 255)',
                                        'color': 'black',
                                        'fontWeight': 'bold',
                                        'textAlign': 'center'
                                    }
                                ],
                                fixed_rows={'headers': True, 'data': 0}
                            ),
                        ],
                        style=layout_table,
                        className="twelve columns"
                    )
                ], className="row",
                style={
                    'margin-top': 10
                }
            ),
            html.Div(
                [
                    html.H3(
                        children='Country Wise Visualization',
                        className='twelve columns',
                        style={
                            'margin-top': 25,
                            'text-align': 'center'
                        }
                    ),
                ], className="row"),
            html.Div(
                [
                    html.Div([
                        html.P(
                            children='Select Country :'
                        ),
                    ], className="six columns"),
                    html.Div([
                        html.P(
                            children='Select Date Range :'
                        ),
                    ], className="six columns")
                ], className="row",
                style={
                    'margin-top': 5
                }
            ),
            html.Div(
                [
                    html.Div([
                        dcc.Dropdown(
                            id='choose_country_dropdown',
                            options=[{"label": i, "value": i} for i in country_population_minus],
                            value='India',
                            style={'position': 'relative', 'zIndex': '999'},
                            placeholder="Select Country",
                            clearable=False
                        )
                    ], className="six columns"),
                    html.Div([
                        dcc.DatePickerRange(
                            id='my-date-picker-range',
                            min_date_allowed=datetime(2020, 1, 22),
                            max_date_allowed=datetime.now(),
                            initial_visible_month=datetime.now(),
                            start_date=datetime.now() - timedelta(days=20),
                            end_date=datetime.now()
                        )
                    ], className="six columns")
                ], className="row"
            ),
            html.Div(
                [
                    html.Div(
                        [
                            dcc.Graph(
                                id='example-graph'

                            )
                        ], className='six columns',
                        style=
                        {
                            'margin-top': '10'
                        }
                    ),
                    html.Div(
                        [
                            html.Div([
                                html.P(
                                    children='Choose the type :'
                                ),
                            ], className="row"),
                            html.Div([
                                dcc.RadioItems(
                                    id="selected_item",
                                    options=[
                                        {'label': 'Confirmed', 'value': 'Confirmed'},
                                        {'label': 'Recovered', 'value': 'Recovered'},
                                        {'label': 'Deaths', 'value': 'Deaths'},
                                        {'label': 'Active', 'value': 'Active'}
                                    ],
                                    value='Confirmed',
                                    labelStyle={'display': 'inline-block'}
                                )
                            ], className="row"),
                            html.Div([
                                dcc.Graph(
                                    id='example-bar'

                                )
                            ], className="row")

                        ], className='six columns',
                        style=
                        {
                            'margin-top': '10'
                        }
                    ),
                ], className='row',
                style={
                    'margin-top': 10
                }
            ),
            html.Div(
                [
                    html.Div([
                        html.H6(
                            children='What may be the reason for such a difference in growth pattern for countries?',
                            className='twelve columns',
                            style={
                                'text-align': 'center'
                            }
                        ),
                    ], className="row"),
                    html.Div([
                        html.Div([
                            dcc.RadioItems(
                                id="selected_factor",
                                options=[
                                    {'label': 'GDP', 'value': 'GDP'},
                                    {'label': 'Sanitation', 'value': 'Sanitation'},
                                    {'label': 'Literacy Rate', 'value': 'Literacy'},
                                    {'label': 'CO2 Emissions', 'value': 'CO2'},
                                    {'label': "International Arrival", 'value': 'IntArrival'},
                                    {'label': "Time Taken To Activate Lockdown", 'value': "Days_Taken_To_Lockdown"}
                                ],
                                value='GDP',
                                labelStyle={'display': 'inline-block'}
                            )
                        ], className="twelve columns",
                            style={
                                'text-align': 'center'
                            }
                        )
                    ], className="row",
                        style={
                            'margin-top': 10,
                        }
                    ),
                    html.Div([
                        html.Div([
                            dcc.Graph(
                                id='example_scatter'
                            )
                        ], className="twelve columns",
                            style={
                                'text-align': 'center'
                            }
                        )
                    ], className="row",
                        style={
                            'margin-top': 10,
                        }
                    ),
                ], className="row",
                style={
                    'margin-top': 10,
                }
            )
        ], className='ten columns offset-by-one',
        style={
            'margin-bottom': 50,
        }
    )
)


# Callback function for dash table country filtration
# Input - value attribute of 'choose_multi_country_dropdown' id which is a multi dropdown
# Output - data attribute of 'datatable' id which is dash table
# NOTE - In place of input parameters, you can give any name, if there is multiple inputs, then it should be in the
# same order as input mentioned in the callback
@app.callback(
    Output('datatable', 'data'),
    [Input('choose_multi_country_dropdown', 'value')])
def update_selected_row_indices(choose_country_dropdown):
    # Copy of the dataframe so that we can filter in a backup dataframe
    map_aux = df_country_popu_minus.copy()

    # Checking if All is present in the dropdown then no need to do any filtration, if not present then we filter by
    # using isin() which checks in a list
    if "All" not in choose_country_dropdown:
        # Country filter
        map_aux = map_aux[map_aux['country'].isin(choose_country_dropdown)]

    # to_dict() makes the dataframe in a readable format for the dash table
    rows = map_aux.to_dict('records')
    return rows


# Callback function for cumulative graph which takes 3 input and gives 1 output
# Input - start_date and end_date attribute from 'my-date-picker-range' id which is a date picker
# Input - value attribute from 'choose_country_dropdown' id which is a single dropdown
# Output - figure attribute for the 'example-graph' id which is a scatter plot
# As said earlier we have multiple inputs so the input parameters are according to the order
@app.callback(
    dash.dependencies.Output('example-graph', 'figure'),
    [dash.dependencies.Input('my-date-picker-range', 'start_date'),
     dash.dependencies.Input('my-date-picker-range', 'end_date'),
     dash.dependencies.Input('choose_country_dropdown', 'value')])
def set_country_date(start_date, end_date, value):
    # start_time and end_time are returned as string from the date picker, so converting it to a yyyy-mm-dd format
    # as datetime object
    # Using re.split() to split the string as the string is in the format of "2020-04-07T21:04:33.717885",
    # the first argument we are mentioning is 'T' as an separator, which will give a list having first element
    # as the year, month, date and the second argument as hour, min, sec, millisec
    start_date = datetime.strptime(re.split('T| ', start_date)[0], '%Y-%m-%d')
    end_date = datetime.strptime(re.split('T| ', end_date)[0], '%Y-%m-%d')

    # Finding the duration
    duration = end_date - start_date

    # days attribute gives the number of days as output
    duration = duration.days

    # Initialising the dataframe with data_backup
    df = pd.DataFrame(data_backup)

    # Taking the one country data and making it a dataframe
    # values attribute changes the dataframe to numpy array which we can change into list and
    # directly pass to the dataframe to make an dataframe object
    df_sub_country = pd.DataFrame(list(df[value].values))

    # iterrows() creates an iterator object which has 2 values, first value as the label or index and
    # 2nd value as one series which is one row
    # Creating an active column
    for lab, row in df_sub_country.iterrows():
        df_sub_country.loc[lab, "active"] = row['confirmed'] - row['deaths'] - row['recovered']

    # Creating the figure object for the scatter plot, layout is the styling part and for data we are creating 4 scatter plot
    # each of which is having an x-axis data, y-axis data, type scatter, name for the scatter plot,
    # mode is lines+markers where the dots are connected with lines
    # x - We are taking the date column which is a series, typecasting as list and using the last duration elements
    # by using negative indexing [start_index(included):end_index(excluded)],
    # here we are not giving end index which means till the last element
    # y - We are taking similarly the confirmed, deaths, recovered, active columns for 4 different scatter plots
    figure = {
        'data':
            [
                {'x': list(df_sub_country['date'])[-duration:], 'y': list(df_sub_country['confirmed'])[-duration:],
                 'type': 'scatter', 'name': 'Confirmed', 'mode': 'lines+markers'},
                {'x': list(df_sub_country['date'])[-duration:], 'y': list(df_sub_country['deaths'])[-duration:],
                 'type': 'scatter',
                 'name': 'Death', 'mode': 'lines+markers'},
                {'x': list(df_sub_country['date'])[-duration:], 'y': list(df_sub_country['recovered'])[-duration:],
                 'type': 'scatter', 'name': 'Recovered', 'mode': 'lines+markers'},
                {'x': list(df_sub_country['date'])[-duration:], 'y': list(df_sub_country['active'])[-duration:],
                 'type': 'scatter',
                 'name': 'Active', 'mode': 'lines+markers'}
            ],
        'layout':
            {
                'title': 'Cumulative',
                'xaxis': dict
                    (
                    title='Date',
                    titlefont=dict
                        (
                        family='Courier New, monospace',
                        size=20,
                        color='#7f7f7f'
                    )
                ),
                'yaxis': dict
                    (
                    title='Number of Cases',
                    titlefont=dict
                        (
                        family='Helvetica, monospace',
                        size=20,
                        color='#7f7f7f'
                    )
                )
            }
    }
    return figure


# Callback function for daily graph which takes 4 input and gives 1 output
# Input - start_date and end_date attribute from 'my-date-picker-range' id which is a date picker
# Input - value attribute from 'choose_country_dropdown' id which is a single dropdown
# Input - value attribute from 'selected_item' id which is a radio button
# Output - figure attribute for the 'example-bar' id which is a bar plot
# As said earlier we have multiple inputs so the input parameters are according to the order
@app.callback(dash.dependencies.Output('example-bar', 'figure'),
              [dash.dependencies.Input('my-date-picker-range', 'start_date'),
               dash.dependencies.Input('my-date-picker-range', 'end_date'),
               dash.dependencies.Input('choose_country_dropdown', 'value'),
               dash.dependencies.Input('selected_item', 'value')])
def set_bar(start_date, end_date, value, value1):
    # start_time and end_time are returned as string from the date picker, so converting it to a yyyy-mm-dd format
    # as datetime object
    # Using re.split() to split the string as the string is in the format of "2020-04-07T21:04:33.717885",
    # the first argument we are mentioning is 'T' as an separator, which will give a list having first element
    # as the year, month, date and the second argument as hour, min, sec, millisec
    start_date = datetime.strptime(re.split('T| ', start_date)[0], '%Y-%m-%d')
    end_date = datetime.strptime(re.split('T| ', end_date)[0], '%Y-%m-%d')

    # Finding the duration
    duration = end_date - start_date

    # days attribute gives the number of days as output
    duration = duration.days

    # Initialising the dataframe with data_backup
    df = pd.DataFrame(data_backup)

    # Initialising the dataframe with data_backup
    df_sub_country = pd.DataFrame(list(df[value].values))

    # iterrows() creates an iterator object which has 2 values, first value as the label or index and
    # 2nd value as one series which is one row
    # Creating an active, confirmed growth, recovered growth, deaths growth, active growth which says the daily trend
    # The logic of lab == 0 is for the first day only, as the growth for 1st day is same as the first day case,
    # then onwards we can subtract the previous day data from the present day to get the daily growth.
    # But for the active growth using the same logic don't make sense, as the active column is always based on
    # the confirmed, recovered and deaths column
    for lab, row in df_sub_country.iterrows():
        df_sub_country.loc[lab, "active"] = row['confirmed'] - row['deaths'] - row['recovered']
        if lab == 0:
            df_sub_country.loc[lab, "confirmed_growth"] = row['confirmed']
            df_sub_country.loc[lab, "recovered_growth"] = row['recovered']
            df_sub_country.loc[lab, "deaths_growth"] = row['deaths']
            df_sub_country.loc[lab, "active_growth"] = df_sub_country.loc[lab, "active"]
        else:
            df_sub_country.loc[lab, "confirmed_growth"] = df_sub_country.loc[lab, "confirmed"] - df_sub_country.loc[
                lab - 1, "confirmed"]
            df_sub_country.loc[lab, "recovered_growth"] = df_sub_country.loc[lab, "recovered"] - df_sub_country.loc[
                lab - 1, "recovered"]
            df_sub_country.loc[lab, "deaths_growth"] = df_sub_country.loc[lab, "deaths"] - df_sub_country.loc[
                lab - 1, "deaths"]
            df_sub_country.loc[lab, "active_growth"] = df_sub_country.loc[lab, "confirmed_growth"] - df_sub_country.loc[
                lab, "recovered_growth"] - df_sub_country.loc[lab, "deaths_growth"]

    # Layout is the css part and for data we are taking the selected item from radio button for y-axis and
    # date in x-axis, type is bar, name is the same as selected
    figure = {
        'data': [
            {'x': list(df_sub_country['date'])[-duration:],
             'y': list(df_sub_country[(value1.lower() + "_growth")])[-duration:], 'type': 'bar', 'name': value1}
        ],
        'layout': {
            'title': 'Daily Trend',
            'xaxis': dict
                (
                title='Date',
                titlefont=dict
                    (
                    family='Courier New, monospace',
                    size=20,
                    color='#7f7f7f'
                )
            ),
            'yaxis': dict
                (
                title='Number of Cases',
                titlefont=dict
                    (
                    family='Helvetica, monospace',
                    size=20,
                    color='#7f7f7f'
                )
            )
        }
    }
    return figure


# This is function for the callback function. It basically implements code reusability.
# It takes 5 inputs and gives 2 output.
# Input - value_inp(input from the radio button), dataframe_factor(dataframe for each factor),
# country_column_name(name of the country column in the dataframe), second_column_name(name of the second column
# whose data we will be plotting), y_axis_title(y-axis title)
# Output - layout(css part), data_scatter(data for the plot)
def help_factor(value_inp, dataframe_factor, country_column_name, second_column_name, y_axis_title):
    # Taking the country names from the pomber's covid19 dataset
    country_available = data1.keys()

    # Here we are taking a common set of countries for which we have data like some countries dont have the covid19 data and
    # similarly for some countries we dont have the population data. So trying to make an intersection but basically giving
    # more focus on the Covid19 data.
    # The same below thing can be done using intersection() of set but for clarity I have used this method.
    country_population_minus1 = list(
        set(country_available) - (set(country_available) - set(list(dataframe_factor[country_column_name]))))

    # Sorting the list as after set manipulation it becomes unordered
    country_population_minus1.sort()

    # Defining a dataFrame for our use which will be only on the filtered countries.
    df_country_factor = pd.DataFrame()

    # Initialising the above by iterating on the filtered countries.
    # enumerate() gives us the index and the value respectively.
    # loc() helps us to assign and get the value at a particular index, it takes row label and column label
    # respectively, here we are using loc() to assign value
    # We are creating 4 columns
    # Same way for country and population column as done in above
    for lab, value in enumerate(country_population_minus1):
        df_country_factor.loc[lab, "country"] = value
        df_country_factor.loc[lab, "population"] = \
            list((population_2020.loc[population_2020['country'] == value])[2020])[0]

        # Taking the selected data from the dataframe_factor in same way using loc(),
        # then going for the required column second_column_name, then as it will be a list so its 0th element
        df_country_factor.loc[lab, value_inp] = list((dataframe_factor.loc[dataframe_factor[country_column_name] ==
                                                                           value])[second_column_name])[0]

        # NOTE - Taking the percentage for each country as it is not fair to take the number of cases, as
        # each country has different population and it is obvious that with a large population the cases will be more.
        # Number of confirmed taken from data1 / population of 2020 * 100
        df_country_factor.loc[lab, "Percentage Of Population Affected"] = data1[value][-1]['confirmed'] / (
            list((population_2020.loc[population_2020['country'] == value])[2020])[0]) * 100

    # Giving the index to country names
    df_country_factor.index = country_population_minus1

    # Only changing the y-axis title as the required selection
    layout = {
        'title': 'Covid 19 Country wise',
        'xaxis': dict
            (
            title='Percentage of cases w.r.t population',
            titlefont=dict
                (
                family='Courier New, monospace',
                size=20,
                color='#7f7f7f'
            )
        ),
        'yaxis': dict
            (
            title=y_axis_title,
            titlefont=dict
                (
                family='Helvetica, monospace',
                size=20,
                color='#7f7f7f'
            ),
            type='log',
            autorange=True,
            tickmode='array',
            tickvals=[1000, 10000, 100000]

        )
    }

    # x-axis is the percentage of population affected( NOTE- The percentage is very small so I am multiplying
    # all the data with 5, list don't allow element-wise multiplication so we are converting the
    # list to a numpy array then multiplying 5 so that it gets multiplied element-wise),
    # y-axis is the same data which is selected(explicit typecasting to list
    # type is scatter plot
    # name - is comparison
    # mode - here is markers(in above we used once lines+markers)

    # NOTE - I personally like this kind of markers which can help you represent another
    # extra data(excluding x-axis and y-axis) in the size of bubbles by using this:-

    # size - size of the markers which here I am setting as the population(as the population for
    # some countries is very huge, so I am taking each element to the power of (1/5), so that I get a
    # proper comparision for all countries, be it small or large(using numpy for element-wise calculation)
    # color - Here you can mention different numbers for different colors(I am using the random.randn() of numpy which
    # creates an list of randon numbers and the input argument is number of element you want to create,
    # so i am passing the length of countries)
    # text - It also takes an list of strings which is displayed when you hover on the markers.
    data_scatter = [
        {'x': np.array(df_country_factor["Percentage Of Population Affected"]) * 5,
         'y': list(df_country_factor[value_inp]), 'type': 'scatter', 'name': 'comparison', 'mode': 'markers',
         'marker': {'size': np.array(df_country_factor['population']) ** (1 / 5),
                    'color': np.random.randn(len(country_population_minus1))}, 'text': country_population_minus1}
    ]
    return layout, data_scatter


# Callback function for reason graph which takes 1 input and gives 1 output
# Input - value attribute from 'selected_factor' id which is a radio button
# Output - figure attribute for the 'example_scatter' id which is a scatter plot
@app.callback(
    Output('example_scatter', 'figure'),
    [Input('selected_factor', 'value')])
def update_factor(value_inp):
    # Checking the value selected in the radio button and according to that reading the
    # dataset(I got from Gapminder) and extracting the necessary columns, then calling the help_factor()
    # Reading using read_excel() of pandas where 1st arg is the name of the file , and 2nd one is optional, if
    # you have more than one sheet then you can mention the sheet name
    if value_inp == "GDP":
        gdp = pd.read_excel('GM-GDP per capita - Dataset - v26.xlsx', sheet_name='gdp')
        gdp_2020 = gdp[['Country Name', 2020]]
        layout, data_scatter = help_factor(value_inp, gdp_2020, 'Country Name', 2020, 'GDP per Capita')

    elif value_inp == "Literacy":
        lliteracy = pd.read_excel('literacy_rate_adult_total_percent_of_people_ages_15_and_above.xlsx')
        lliteracy_2020 = lliteracy[['country', 2011]]
        layout, data_scatter = help_factor(value_inp, lliteracy_2020, 'country', 2011,
                                           'Literacy Rate aged 15 and Above')

    elif value_inp == "CO2":
        co2 = pd.read_excel('co2_emissions_tonnes_per_person.xlsx')
        co2_2020 = co2[['country', 2014]]
        layout, data_scatter = help_factor(value_inp, co2_2020, 'country', 2014,
                                           'CO2 Emissions Tonnes Per Person')

    elif value_inp == "Sanitation":
        sanitation = pd.read_excel('at_least_basic_sanitation_overall_access_percent.xlsx')
        sanitation_2020 = sanitation[['country', 2015]]
        layout, data_scatter = help_factor(value_inp, sanitation_2020, 'country', 2015,
                                           'Basic Sanitation Overall Access Percent')

    elif value_inp == 'IntArrival':
        international_travellers_arrival = pd.read_excel('st_int_arvl.xlsx')
        international_travellers_arrival_2020 = international_travellers_arrival[['country', 2018]]
        layout, data_scatter = help_factor(value_inp, international_travellers_arrival_2020, 'country', 2018,
                                           'International Travel Arrival')

    # This part of the code could not be incorporated in the help_factor() as it has some extra code
    elif value_inp == 'Days_Taken_To_Lockdown':
        # Reading the dataset using read_csv() of pandas
        # This dataset I got from kaggle - https://www.kaggle.com/jcyzag/covid19-lockdown-dates-by-country/data#countryLockdowndatesJHUMatch.csv
        lockdown_date = pd.read_csv('countryLockdowndates.csv')
        lockdown_date_2020 = lockdown_date[['Country/Region', 'Date', 'Type']]

        # Removing the Nan data elements
        lockdown_date_2020 = lockdown_date_2020.dropna()

        # Taking backup
        data5 = lockdown_date_2020

        # drop_duplicates() removes the duplicates records(if there), subset attribute is optional, means
        # it has to check only for suplicates in Contry/Region column and if found then remove that row.
        # In general if not given this argument then it compare whole row to find duplicacy.
        data5.drop_duplicates(subset='Country/Region',
                              keep=False, inplace=True)
        # Taking country name, taking intersection then sorting as we have done in above many times.
        country_available = data1.keys()
        country_population_minus1 = list(
            set(country_available) - (set(country_available) - set(list(data5['Country/Region']))))
        country_population_minus1.sort()
        df_country_factor = pd.DataFrame()

        # Extra part of code from other
        # Here for each country we are taking the date in which first case was detected,
        # and time taken in days to activate the lockdown
        df1 = pd.DataFrame(data_backup)

        # Iterating on each country
        for i in country_population_minus1:
            # Making a dataframe for each country separately
            df_sub_country = pd.DataFrame(list(df1[i].values))

            # Defining a variable for storing the date_first
            date_first = ""

            # Iterating over the country dataframe using iterrows()
            for lab, row in df_sub_country.iterrows():
                # Here the logic is when we find that the number of confirmed cases is more than 0, we are breaking and
                # taking the date for that ,as it will be the first case detected
                if row['confirmed'] > 0:
                    date_first = row['date']
                    break

            # Getting the index so that we can store
            index = data5.index[data5['Country/Region'] == i].tolist()[0]

            # Storing the first case detected
            data5.loc[index, "first_case_detected"] = date_first

            # Converting it to datetime object from string then taking a difference and getting
            # the number of days, storing it to the dataframe under days_taken_to_lockdown
            data5.loc[index, "days_taken_to_lockdown"] = (
                    datetime.strptime(data5.loc[index, "Date"], '%d/%m/%Y') - datetime.strptime(date_first,
                                                                                                '%Y-%m-%d')).days

        # There is some data which shows that lockdown was first done then the first case was detected.
        # For me it is kind of outlier that why i am removing it.
        data5 = data5[data5['days_taken_to_lockdown'] > 0]

        # Some rows are removed so again filtering the names of teh country and sorting it
        country_available = data1.keys()
        country_population_minus1 = list(
            set(country_available) - (set(country_available) - set(list(data5['Country/Region']))))
        country_population_minus1.sort()

        country_list = []

        # Creating 6 columns and storing the data accodingly, the if condition is for some countries which was not
        # present in population dataset, which was a rare issue as it was the larger dataset
        # having almost all countries data.
        for lab, value in enumerate(country_population_minus1):
            if value in list(population_2020['country']):
                country_list.append(value)
                df_country_factor.loc[lab, "country"] = value
                df_country_factor.loc[lab, "population"] = \
                    list((population_2020.loc[population_2020['country'] == value])[2020])[0]
                df_country_factor.loc[lab, "lockdown_date"] = \
                    list((data5.loc[data5['Country/Region'] == value])['Date'])[0]
                df_country_factor.loc[lab, "first_case_detected"] = \
                    list((data5.loc[data5['Country/Region'] == value])['first_case_detected'])[0]
                df_country_factor.loc[lab, value_inp] = \
                    list((data5.loc[data5['Country/Region'] == value])['days_taken_to_lockdown'])[0]
                df_country_factor.loc[lab, "Percentage Of Population Affected"] = data1[value][-1]['confirmed'] / (
                    list((population_2020.loc[population_2020['country'] == value])[2020])[0]) * 100

        df_country_factor.index = country_list

        # Same as helper_factor() function
        layout = {
            'title': 'Covid 19 Country wise',
            'xaxis': dict
                (
                title='Percentage of cases w.r.t population',
                titlefont=dict
                    (
                    family='Courier New, monospace',
                    size=20,
                    color='#7f7f7f'
                )
            ),
            'yaxis': dict
                (
                title='Lockdown Date - FirstCase Detected Date(Days)',
                titlefont=dict
                    (
                    family='Helvetica, monospace',
                    size=20,
                    color='#7f7f7f'
                ),
                type='log',
                autorange=True,
                tickmode='array',
                tickvals=[1000, 10000, 100000]

            )
        }
        data_scatter = [
            {'x': np.array(df_country_factor["Percentage Of Population Affected"]) * 5,
             'y': list(df_country_factor[value_inp]), 'type': 'scatter', 'name': 'comparison', 'mode': 'markers',
             'marker': {'size': np.array(df_country_factor['population']) ** (1 / 5),
                        'color': np.random.randn(len(country_population_minus1))}, 'text': country_population_minus1}
        ]

    # After getting the data_scatter and layout for any of the matched case from the radio item we are just
    # assigning the same and returning to the plot.
    figure = {
        'data': data_scatter,
        'layout': layout
    }

    return figure


# Callback for Reset Button, which takes 2 input and gives 1 output
# Input - n_clicks, n_clicks_timestamp attribute of submit-val id which is a button
# Output - style attribute of placeholder id which is a paragraph

# NOTE - In dash it is mandatory to have atleast one input and atleast one output for a callback. So I had to make a
# paragraph for this callback output whcih is totally unnecessary that is the reason I have set the display as none.

# Basically this callback is to reload the data again from pomber's covid19 dataset.
@app.callback(
    dash.dependencies.Output('placeholder', 'style'),
    [dash.dependencies.Input('submit-val', 'n_clicks'),
     dash.dependencies.Input('submit-val', 'n_clicks_timestamp')])
def update_output(n_clicks, timestammp_clicks):
    # Defining the style for the dummy paragraph element.
    style = {
        'float': 'right'}

    # Saving the current time when the button was pressed
    present_server_datetime = datetime.now()

    # Using global keyword which specifies that now we can change the data of the global variable. If we don't
    # use global keyword, then we can access the global data but we cannot change the data in that variable as
    # we are in local scope.
    global data1, data_backup, df, population, population_2020, country_available, country_population_minus, \
        df_country_popu_minus, current_server_startime

    # Checking with the logic if there is a difference of 6 hrs, then only allowing to reload the data, otherwise
    # many of us will go on clicking the button and the server will unnecessarily reload the data.
    # This is my logic, you can implement your logic.
    # Here total_seconds() changes the duration to seconds, then dividing it with 3600 to get the hour.
    if divmod((present_server_datetime - current_server_startime).total_seconds(), 3600)[0] > 6:

        # Reseeting the current server time
        current_server_startime = present_server_datetime

        # Reading the pomber's covid19 data. Using a try catch block so that if someday pomber's link had some
        # issue we can get that in our server.
        try:
            data1 = requests.get("https://pomber.github.io/covid19/timeseries.json")
        except Exception as e:
            print(e)

        data1 = data1.json()

        # Storing as a backup in one json file. For that json.dump() is used, 1st arg is data, 2nd arg is the
        # filehandler, 3rd one is optional - indent.
        with open('data_pomber.json', 'w') as filehandle:
            json.dump(data1, filehandle, indent=4)

        # Taking backup of data1
        data_backup = dict(data1)

        # We are doing the same things that are done above which I have already explained, here as we using global
        # and the same variable names so it gets updated in the global scope also.
        df = pd.DataFrame(data_backup)

        population = pd.read_excel('population_total.xlsx')

        population_2020 = population[['country', 2020]]
        country_available = data1.keys()
        country_population_minus = list(
            set(country_available) - (set(country_available) - set(list(population_2020['country']))))
        country_population_minus.sort()
        df_country_popu_minus = pd.DataFrame()

        for lab, value in enumerate(country_population_minus):
            df_country_popu_minus.loc[lab, "country"] = value
            # data1[country_name] gives a list, from that we are taking the last element(by -ve indexing) which is the latest date
            df_country_popu_minus.loc[lab, "confirmed"] = data1[value][-1]['confirmed']
            # population_2020.loc[population_2020['country'] == value] gives us a dataframe where the country is same as value,
            # from that we are taking the 2020 column, which again gives us a series(explicitly typecasting it to list so that
            # we can do indexing) list which has only one element, so we are using the 0th element
            df_country_popu_minus.loc[lab, "population"] = \
                list((population_2020.loc[population_2020['country'] == value])[2020])[0]
            df_country_popu_minus.loc[lab, "recovered"] = data1[value][-1]['recovered']
            df_country_popu_minus.loc[lab, "death"] = data1[value][-1]['deaths']
            df_country_popu_minus.loc[lab, "active"] = data1[value][-1]['confirmed'] - data1[value][-1]['deaths'] - \
                                                       data1[value][-1]['recovered']

        df_country_popu_minus.index = country_population_minus

    return style


# Running the server with main
if __name__ == '__main__':
    app.run_server(debug=True)
