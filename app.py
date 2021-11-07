## The dash code will be here

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
from dash import dcc
from dash import html
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.tools as tls
import datetime

# Disable future warnings
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

date = datetime.date.today()-datetime.timedelta(days=365)
date = date.strftime("%m-%d-%Y")
path = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{}.csv'.format(date)
df = pd.read_csv(path)

df.drop(['FIPS', 'Admin2','Last_Update','Province_State', 'Combined_Key'], axis=1, inplace=True)
df.rename(columns={'Country_Region': "Country"}, inplace=True)
world = df.groupby("Country")['Confirmed','Active','Recovered','Deaths'].sum().reset_index()
world.head(10)

data = world.drop(["Active", "Recovered"], axis=1)
figScatter = px.scatter(data, x="Confirmed", y="Deaths", hover_data=["Country"], color="Confirmed", title="Interactive Scatter Map w/ Confirmed and Death Cases", template="plotly_dark")

figMap = px.choropleth(world,locations="Country", locationmode="country names", color="Confirmed", hover_name="Country",title="Interactive Choropleth Map w/ Confirmed Cases", template='plotly_dark', )

### Find top 20 countries with maximum number of confirmed cases
top_20 = world.sort_values(by=['Confirmed'], ascending=False).head(20)

### Generate a Barplot
fig = plt.figure()
plot = sns.barplot(top_20['Confirmed'], top_20['Country'])
for i,(value,name) in enumerate(zip(top_20['Confirmed'],top_20['Country'])):
    plot.text(value,i-0.05,name + ":\t" + f'{value:,.0f}')
barplotConfirmed = tls.mpl_to_plotly(fig)

### Find top 20 countries with maximum number of confirmed cases
top_20 = world.sort_values(by=['Deaths'], ascending=False).head(20)

### Generate a Barplot
fig = plt.figure()
plot = sns.barplot(top_20['Deaths'], top_20['Country'])
for i,(value,name) in enumerate(zip(top_20['Deaths'],top_20['Country'])):
    plot.text(value,i-0.05,name + ":\t" + f'{value:,.0f}')
barplotDeaths = tls.mpl_to_plotly(fig)

external_stylesheets =  ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, title='COVID-19 Visualisation')

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app.layout = html.Div(children=[
                html.H1(children='COVID-19 Visualisation w/ Plotly Dash'),

                html.Div([
                    html.Div([

                        html.H3(children='Interactive Scatter Map w/ Confirmed and Death Cases'),
                        dcc.Graph(
                            id='scatterPlot',
                            figure=figScatter
                        ), 

                    ], className='six columns userInput'),
                    html.Div([

                        html.H3(children='Interactive Choropleth Map w/ Confirmed Cases'),
                        dcc.Graph(
                            id='mapPlot',
                            figure=figMap
                        ),  

                    ], className='six columns'),
                ], className='row'),

                html.Div([
                    html.Div([

                        html.H3(children='Top 20 Countries (Confirmed Cases)'),
                        dcc.Graph(
                            id='plot1',
                            figure=barplotConfirmed
                        ), 

                    ], className='six columns userInput'),
                    html.Div([

                        html.H3(children='Top 20 Countries (Death Cases)'),
                        dcc.Graph(
                            id='plot2',
                            figure=barplotDeaths
                        ),  

                    ], className='six columns'),
                ], className='row'),
            ])

if __name__ == '__main__':
    app.run_server(debug=True)
