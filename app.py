import pandas as pd
import numpy as np
import plotly.express as px
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from us_state_abbrev import us_state_abbrev
from datetime import date
import utils
from urllib.request import urlopen
# import json
# with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
#     counties = json.load(response)


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

timeseries = utils.load_state_timeseries()

app.layout = html.Div([
    html.H2('US Coronavirus States Map', style={'textAlign': 'center'}),
    html.Div(
        html.P([
            'Select case type: ',
            dcc.RadioItems(
                id='case-type-radio',
                options=[
                    {'label': 'Confirmed', 'value': 'Confirmed'},
                    {'label': 'Deaths', 'value': 'Deaths'},
                    {'label': 'Recovered', 'value': 'Recovered'},
                    {'label': 'Active', 'value': 'Active'}
                ],
                value='Confirmed',
                labelStyle={'display': 'inline-block'}
            ),
            'Select a date: ',
            dcc.DatePickerSingle(
                id='date-slider',
                month_format='MMM-Do-YY',
                min_date_allowed=date(2020, 3, 10),
                max_date_allowed=date.today(),
                initial_visible_month=date(2020, 3, 23),
                date=date(2020, 3, 23),
                style={'display': 'inline-block'}
            )
        ],
        style={'textAlign': 'center'}
        ),
    ),
    dcc.Graph(id='map-with-slider'),
    html.H2('Trend', style={'textAlign': 'center'}),
    dcc.Graph(
        id='trend',
        # figure=px.line(timeseries, )
    )
])


@app.callback(
    Output("map-with-slider", "figure"), 
    [Input('case-type-radio', 'value'), Input('date-slider', 'date')]
    )
def update_map(case_type, selected_date):
    y, m, d = selected_date.split('-')
    report = utils.load_state_daily_report(m+'-'+d+'-'+y)
    if pd.to_datetime(selected_date) <= pd.to_datetime('03-22-2020'):
        fig = px.choropleth(report, locationmode='USA-states',
                                color = np.log10(report[case_type]),
                                locations=report['Province/State'],
                                hover_data=['Confirmed', 'Deaths', 'Recovered', 'Active'], 
                                hover_name='Province/State',
                                color_continuous_scale='GnBu'#['green','yellow','orange','red']
                            )

        fig.update_layout(
                showlegend = True,
                geo_scope='usa',
                coloraxis_colorbar=dict(
                    title='# of Cases',
                    tickvals=[1, 2, 3, 4, 5],
                    ticktext=['10', '100', '1k', '10k','100k'],
                ),
                margin={"r":0,"t":0,"l":0,"b":0}
            )
    else:
        # report = report[report[case_type]>0]
        report = report.sort_values(case_type)
        fig = px.scatter_geo(report, lat=report['Lat'], lon=report['Long_'], scope='usa',
                                color = np.log10(report[case_type]+1),opacity=0.8,
                                # size = report[case_type]**0.35*10,
                                # locations='FIPS',
                                hover_data=['Confirmed', 'Deaths', 'Recovered', 'Active'], 
                                hover_name='Combined_Key',
                                color_continuous_scale='YlOrRd'#['green','yellow','orange','red']
                            )
        fig.update_layout(
                showlegend = True,
                geo_scope='usa',
                coloraxis_colorbar=dict(
                    title='# of Cases',
                    tickvals=[0, 1, 2, 3, 4],
                    ticktext=['0', '10', '100', '1k','10k'],
                ),
                margin={"r":0,"t":0,"l":0,"b":0}
            )
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)