import pandas as pd
import numpy as np
import plotly.express as px
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from us_state_abbrev import us_state_abbrev
from datetime import date, timedelta
import utils
from urllib.request import urlopen
# import json
# with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
#     counties = json.load(response)

template='plotly_dark'
colors = {
    'background': '#202020',
    'text': 'white',
    'header': 'white'
}
shadow = '3px 3px 5px 6px rgba(0, 0, 0, 0.4)'

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# app.css.append_css({
#     'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
# })

timeseries = utils.load_state_timeseries()

trend_confirmed = px.area(timeseries['confirmed'], x='date', y='Number of Cases', 
                            color='Province/State', template=template, title='Number of Confirmed Cases')

trend_deaths = px.area(timeseries['deaths'], x='date', y='Number of Cases',
                            color='Province/State', template=template, title='Number of Deaths')

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    
    html.Div(style={'backgroundImage':'url(https://harfordcountyhealth.com/wp-content/uploads/2020/01/home-banner.jpg)',
                'box-shadow': '3px 3px 5px 6px rgba(0, 0, 0, 0.4)',
                'height': '150px'}, children=[
        html.H1('US Coronavirus Dashboard', className='row', 
            style={'textAlign': 'center', 'verticalAlign':'middle', 'padding':'40px', 'color':colors['header'], 
        }
    )
    ]), 
    
    html.Br(),

    # html.H4(children='Case Distribution Map', style={
    #     'textAlign': 'center',
    #     'color': colors['header']
    # }),

    html.Div(className='row', style={'padding-left':'10%', 'padding-right':'10%'}, children=[
        html.Div(className='two columns', children=[
            html.Label('Select Case Type:', style={'color':colors['text']}), 
            dcc.RadioItems(
                id='case-type-radio',
                style={'color':colors['text']},
                options=[
                    {'label': 'Confirmed', 'value': 'Confirmed'},
                    {'label': 'Deaths', 'value': 'Deaths'},
                    {'label': 'Recovered', 'value': 'Recovered'},
                    {'label': 'Active', 'value': 'Active'}
                ],
                value='Confirmed'
            ),
            html.Br(),
            html.Label('Select Date: ', style={'color':colors['text']}),
            dcc.DatePickerSingle(
                id='date-slider',
                style={'color':colors['text']},
                month_format='MMM-Do-YY',
                min_date_allowed=date(2020, 3, 10),
                max_date_allowed=date.today()-timedelta(days=1),
                initial_visible_month=date.today()-timedelta(days=1),
                date=date.today()-timedelta(days=1)
            )
        ])
        ,
        dcc.Graph(id='map', className='ten columns', style={'box-shadow': shadow}),
    ]),

    html.Br(),
    # html.H4(children='Trend By States', style={
    #     'textAlign': 'center',
    #     'color': colors['header']
    # }),
    html.Div(className='row', style={'padding-left': '10%', 'padding-right':'10%'}, children=[
        dcc.Graph(
            id='trend-confirmed',
            className='six columns',
            figure=trend_confirmed,
            style={'box-shadow': shadow}
        ),
        dcc.Graph(
            id='trend-deaths',
            className='six columns',
            figure=trend_deaths,
            style={'box-shadow': shadow}
        )
    ])
])


@app.callback(
    Output("map", "figure" ), 
    [Input('case-type-radio', 'value'), Input('date-slider', 'date')]
    )
def update_map(case_type, selected_date):
    y, m, d = selected_date.split('-')
    report = utils.load_state_daily_report(m+'-'+d+'-'+y)
    if pd.to_datetime(selected_date) <= pd.to_datetime('03-22-2020'):
        fig = px.choropleth(
            report, 
            locationmode='USA-states',
            color = np.log10(report[case_type]),
            locations=report['Province/State'],
            hover_data=['Confirmed', 'Deaths', 'Recovered', 'Active'], 
            hover_name='Province/State',
            color_continuous_scale='YlOrRd',
            template=template
        )
        fig.update_layout(
                showlegend = True,
                geo_scope='usa',
                coloraxis_colorbar=dict(
                    title='# of Cases',
                    tickvals=[1, 2, 3, 4, 5],
                    ticktext=['10', '100', '1k', '10k','100k'],
                    len=0.75, thickness=10
                ),
                margin={"r":0,"t":0,"l":0,"b":0}
        )
    else:
        # report = report[report[case_type]>0]
        report = report.sort_values(case_type)
        fig = px.scatter_geo(
            report, title='Case Distribution Map',
            lat=report['Lat'], lon=report['Long_'], scope='usa',
            color = np.log10(report[case_type]+1),opacity=0.75,
            size = report[case_type]**0.5,
            # locations='FIPS',
            hover_data=['Confirmed', 'Deaths', 'Recovered', 'Active'], 
            hover_name='Combined_Key',
            color_continuous_scale='YlOrRd',
            template=template,
        )
        fig.update_layout(
            showlegend = True,
            geo_scope='usa',
            coloraxis_colorbar=dict(
                title='# of Cases',
                tickvals=[0, 1, 2, 3, 4],
                ticktext=['0', '10', '100', '1k','10k'],
                len=0.75, thickness=10

            ),
            margin={"r":0,"t":75,"l":0,"b":0}
        )
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)