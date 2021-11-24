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
    path = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{}.csv'.format(date)
    df = pd.read_csv(path)

    df.drop(['FIPS', 'Admin2','Last_Update','Province_State', 'Combined_Key'], axis=1, inplace=True)
    df.rename(columns={'Country_Region': "Country"}, inplace=True)
    world = df.groupby("Country")['Confirmed','Active','Recovered','Deaths'].sum().reset_index()
    
    dailyStatistics = [world['Confirmed'].sum(), world['Deaths'].sum(), world['Confirmed'].mean(), world['Deaths'].mean()]

    data = world.drop(["Active", "Recovered"], axis=1)
    figScatter = px.scatter(data, x="Confirmed", y="Deaths", hover_data=["Country"], color="Confirmed", title="Interactive Scatter Map w/ Confirmed and Death Cases", template="plotly_dark")

    figMap = px.choropleth(world,locations="Country", locationmode="country names", color="Confirmed", hover_name="Country",title="Interactive Choropleth Map w/ Confirmed Cases", template='plotly_dark', )

    ### Find top 20 countries with maximum number of confirmed cases
    top_20 = world.sort_values(by=['Confirmed'], ascending=False).head(20)

    ### Generate a Barplot
    barplotConfirmed = px.bar(top_20, x='Confirmed', y='Country', template="plotly_dark")

    ### Find top 20 countries with maximum number of confirmed cases
    top_20 = world.sort_values(by=['Deaths'], ascending=False).head(20)

    ### Generate a Barplot
    barplotDeaths = px.bar(top_20, x='Deaths', y='Country', template="plotly_dark")
    
    return figScatter, figMap, barplotConfirmed, barplotDeaths, dailyStatistics

external_stylesheets =  ['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.DARKLY]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, title='COVID-19 Visualisation')

app.layout = html.Div(children=[
                html.Div([
                    html.H1(children='COVID-19 Visualisation using Plotly Dash'),
                ], className='row', style={'text-align':'center', 'padding':'10px'}) ,
                html.Div([
                    html.H3('Pick date to view:'),
                    dcc.DatePickerSingle(
                        id='date-picker',
                        display_format = 'DD/MM/YYYY',
                        min_date_allowed=datetime.date(2020, 3, 22),
                        max_date_allowed= datetime.date.today() - datetime.timedelta(days=1),
                        date= datetime.date.today() - datetime.timedelta(days=1),
                        style={'font-size':'15px'},
                    ),
                ], className='row', style={'text-align':'center'}) ,
                html.Div([
                    html.H3(id='output-data'),
                ], className='row', style={'text-align':'center', 'padding-top':'15px'}) ,
                html.Div([
                    html.Div([
                        html.H2(children='Interactive Scatter Map w/ Confirmed and Death Cases'),
                        dcc.Graph(
                            id='scatterPlot',
                        ), 
                    ], className='six columns userInput', style={'text-align':'center'}),
                    html.Div([
                        html.H2(children='Interactive Choropleth Map w/ Confirmed Cases'),
                        dcc.Graph(
                            id='mapPlot',
                        ),  
                    ], className='six columns', style={'text-align':'center'}),
                ], className='row', style={'padding':'15px'}),

                html.Div([
                    html.Div([
                        html.H2(children='Top 20 Countries (Confirmed Cases)'),
                        dcc.Graph(
                            id='barConfirmed',
                        ), 
                    ], className='six columns', style={'text-align':'center'}),
                    html.Div([
                        html.H2(children='Top 20 Countries (Death Cases)'),
                        dcc.Graph(
                            id='barDeaths',
                        ),  
                    ], className='six columns', style={'text-align':'center'}),
                ], className='row', style={'padding':'15px'}),
            ])

@app.callback(
    Output('output-data', 'children'),
    Output('scatterPlot', 'figure'),
    Output('mapPlot', 'figure'),
    Output('barConfirmed', 'figure'),
    Output('barDeaths', 'figure'),
    Input('date-picker', 'date'))
def update_output(date_value):
    selection = 'Date Selected: '
    if date_value is not None:
        date_object = datetime.date.fromisoformat(date_value)
        date_string = date_object.strftime('%m-%d-%Y')
        date_text_string = date_object.strftime('%B %d, %Y')

        try:
            path = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{}.csv'.format(date_string)
            pd.read_csv(path)
        except:
              return 'Data Not Available', px.bar(), px.bar(), px.bar(), px.bar(), 

        scatterPlot, mapPlot, barConfirmed, barDeaths, graphStatistics= get_graphs(date_string)

        statistics = html.Table([
                                    html.Tr([html.Td("Date Selected: "), html.Td(date_text_string)]),
                                    html.Tr([html.Td("Total Confirmed: "), html.Td(f"{graphStatistics[0]:,}")]),
                                    html.Tr([html.Td("Total Deaths: "), html.Td(f"{graphStatistics[1]:,}")]),
                                    html.Tr([html.Td("Mean Confirmed: "), html.Td(f"{round(graphStatistics[2],2):,}")]),
                                    html.Tr([html.Td("Mean Deaths: "), html.Td(f"{round(graphStatistics[3],2):,}")]),
                                    html.Tr([html.Td("Ratio (Confirmed:Deaths): "), html.Td(f"{round(graphStatistics[0]/graphStatistics[1],2):,}")]),                  
                    ], style={'marginLeft': 'auto', 'marginRight': 'auto'}),
        
        return statistics, scatterPlot, mapPlot, barConfirmed, barDeaths

if __name__ == '__main__':
    app.run_server(debug=True)