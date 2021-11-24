import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import plotly.express as px
import datetime

# Disable future warnings
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


def get_graphs(date):
    # Read raw csv file from GitHub repo and save into dataframe. User
    # specifies date for daily report.
    path = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{}.csv'.format(
        date)
    df = pd.read_csv(path)

    # Removing unused attributes (Usually missing data)
    df.drop(['FIPS',
             'Admin2',
             'Last_Update',
             'Province_State',
             'Combined_Key'],
            axis=1,
            inplace=True)

    # Rename headers
    df.rename(columns={'Country_Region': "Country"}, inplace=True)

    # Order data by country
    world = df.groupby("Country")[
        'Confirmed',
        'Active',
        'Recovered',
        'Deaths'].sum().reset_index()

    # Gather daily statistics including total confirmed cases, total death
    # cases, mean confirmed cases, mean death cases and ratio between total
    # confirmed and total death cases.
    dailyStatistics = [
        world['Confirmed'].sum(),
        world['Deaths'].sum(),
        world['Confirmed'].mean(),
        world['Deaths'].mean()]

    # Plot scatter chart using confirmed and death cases
    figScatter = px.scatter(
        world,
        x="Confirmed",
        y="Deaths",
        hover_data=["Country"],
        color="Confirmed",
        title="Interactive Scatter Map w/ Confirmed and Death Cases",
        template="plotly_dark")

    # Plot world map showing heatmap of confirmed cases in each country.
    figMap = px.choropleth(
        world,
        locations="Country",
        locationmode="country names",
        color="Confirmed",
        hover_name="Country",
        title="Interactive Choropleth Map w/ Confirmed Cases",
        template='plotly_dark',
    )

    # Find top 20 countries with maximum number of confirmed cases
    top_20 = world.sort_values(by=['Confirmed'], ascending=False).head(20)

    # Plot bar graph with top 20 countries with highest confirmed cases
    barplotConfirmed = px.bar(
        top_20,
        x='Confirmed',
        y='Country',
        template="plotly_dark")

    # Plot pie chart using top 20 countries confirmed cases
    pieConfirmed = px.pie(
        top_20,
        values='Confirmed',
        names='Country',
        template="plotly_dark")

    # Find top 20 countries with maximum number of death cases
    top_20 = world.sort_values(by=['Deaths'], ascending=False).head(20)

    # Plot bar graph with top 20 countries with highest death cases
    barplotDeaths = px.bar(
        top_20,
        x='Deaths',
        y='Country',
        template="plotly_dark")

    # Plot pie chart using top 20 countries death cases
    pieDeath = px.pie(
        top_20,
        values='Deaths',
        names='Country',
        template="plotly_dark")

    # Return all graphs and statistics
    return figScatter, figMap, barplotConfirmed, barplotDeaths, pieConfirmed, pieDeath, dailyStatistics


# CSS for dark theme and bootstrap functions
external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    dbc.themes.DARKLY]

# Initialise Dash session
app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    title='COVID-19 Visualisation')

# Layout of Dash application
app.layout = html.Div(children=[
    # Title
    html.Div([
        html.H1(children='COVID-19 Visualisation using Plotly Dash'),
    ], className='row', style={'text-align': 'center', 'padding': '10px'}),

    # Pick date to view
    html.Div([
        html.H3('Pick date to view:'),
        dcc.DatePickerSingle(
            id='date-picker',
            display_format='DD/MM/YYYY',
            min_date_allowed=datetime.date(2020, 3, 22),
            max_date_allowed=datetime.date.today() - datetime.timedelta(days=1),
            date=datetime.date.today() - datetime.timedelta(days=1),
            style={'font-size': '15px'},
        ),
    ], className='row', style={'text-align': 'center'}),

    # Daily statistics
    html.Div([
        html.H3(id='output-data'),
    ], className='row', style={'text-align': 'center', 'padding-top': '15px'}),

    # Scatter graph and map
    html.Div([

        # Interactive Scatter Map w/ Confirmed and Death Cases
        html.Div([
            html.H2(
                children='Interactive Scatter Map w/ Confirmed and Death Cases'),
            dcc.Graph(
                id='scatterPlot',
            ),
        ], className='six columns userInput', style={'text-align': 'center'}),

        # Interactive Choropleth Map w/ Confirmed Cases
        html.Div([
            html.H2(children='Interactive Choropleth Map w/ Confirmed Cases'),
            dcc.Graph(
                id='mapPlot',
            ),
        ], className='six columns', style={'text-align': 'center'}),
    ], className='row', style={'padding': '15px'}),

    # Top 20 bar charts
    html.Div([

        # Confirmed cases
        html.Div([
            html.H2(children='Top 20 Countries (Confirmed Cases)'),
            dcc.Graph(
                id='barConfirmed',
            ),
        ], className='six columns', style={'text-align': 'center'}),

        # Death cases
        html.Div([
            html.H2(children='Top 20 Countries (Death Cases)'),
            dcc.Graph(
                id='barDeaths',
            ),
        ], className='six columns', style={'text-align': 'center'}),
    ], className='row', style={'padding': '15px'}),

    html.Div([

        # Pie Chart - Confirmed Cases
        html.Div([
            html.H2(children='Pie Chart for Top 20 Countries (Confirmed Cases)'),
            dcc.Graph(
                id='pieConfirmed',
            ),
        ], className='six columns', style={'text-align': 'center'}),

        # Pie Chart - Death Cases
        html.Div([
            html.H2(children='Pie Chart forTop 20 Countries (Death Cases)'),
            dcc.Graph(
                id='pieDeaths',
            ),
        ], className='six columns', style={'text-align': 'center'}),
    ], className='row', style={'padding': '15px'}),
])

# Callbacks for user input (Updates data)


@app.callback(
    Output('output-data', 'children'),
    Output('scatterPlot', 'figure'),
    Output('mapPlot', 'figure'),
    Output('barConfirmed', 'figure'),
    Output('barDeaths', 'figure'),
    Output('pieConfirmed', 'figure'),
    Output('pieDeaths', 'figure'),
    Input('date-picker', 'date'))
def update_output(date_value):

    # Check if data is valid and convert to string formats needed
    if date_value is not None:
        date_object = datetime.date.fromisoformat(date_value)
        date_string = date_object.strftime('%m-%d-%Y')
        date_text_string = date_object.strftime('%B %d, %Y')

        # Check if file is available, can get 404 error so return data is not
        # available. Graphs are empty if file is not available.
        try:
            path = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{}.csv'.format(
                date_string)
            pd.read_csv(path)
        except BaseException:
            return 'Data Not Available', px.bar(), px.bar(), px.bar(), px.bar(),

        # Get graphs using user's selected date
        scatterPlot, mapPlot, barConfirmed, barDeaths, pieConfirmed, pieDeath, graphStatistics = get_graphs(
            date_string)

        # Display daily statistics gathered from get_graph()
        statistics = html.Table([
            html.Tr([html.Td("Date Selected: "), html.Td(date_text_string)]),
            html.Tr([html.Td("Total Confirmed: "), html.Td(f"{graphStatistics[0]:,}")]),
            html.Tr([html.Td("Total Deaths: "), html.Td(f"{graphStatistics[1]:,}")]),
            html.Tr([html.Td("Mean Confirmed: "), html.Td(f"{round(graphStatistics[2],2):,}")]),
            html.Tr([html.Td("Mean Deaths: "), html.Td(f"{round(graphStatistics[3],2):,}")]),
            html.Tr([html.Td("Ratio (Confirmed:Deaths): "), html.Td(f"{round(graphStatistics[0]/graphStatistics[1],2):,}")]),
        ], style={'marginLeft': 'auto', 'marginRight': 'auto'}),

        # Return graphs and statistics as Outputs
        return statistics, scatterPlot, mapPlot, barConfirmed, barDeaths, pieConfirmed, pieDeath


# Main loop to run live server
if __name__ == '__main__':
    app.run_server(debug=True)
