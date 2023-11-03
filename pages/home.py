"""Content of the home page, with buttons to various parts of the webapp."""
import logging

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dcc, html
from dash.development.base_component import Component
from redis import Redis
from redis.exceptions import RedisError
import requests

from dash_app.conf import REDIS_HOST, REDIS_PORT, SENSOR_HOST
from pages import templates

REDIS_CONN = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT  # default
)
"""Provides an connection to the redis server at ``redis://<REDIS_HOST>:<REDIS_PORT>``."""

dash.register_page(__name__, title='Homepage', path='/')

# pylint: disable=line-too-long
#########################################################################################################
##     ######   #######  ##     ## ########   #######  ##    ## ######## ##    ## ########  ######     ##
##    ##    ## ##     ## ###   ### ##     ## ##     ## ###   ## ##       ###   ##    ##    ##    ##    ##
##    ##       ##     ## #### #### ##     ## ##     ## ####  ## ##       ####  ##    ##    ##          ##
##    ##       ##     ## ## ### ## ########  ##     ## ## ## ## ######   ## ## ##    ##     ######     ##
##    ##       ##     ## ##     ## ##        ##     ## ##  #### ##       ##  ####    ##          ##    ##
##    ##    ## ##     ## ##     ## ##        ##     ## ##   ### ##       ##   ###    ##    ##    ##    ##
##     ######   #######  ##     ## ##         #######  ##    ## ######## ##    ##    ##     ######     ##
#########################################################################################################
# pylint: enable=line-too-long


def card_sensors() -> dbc.Card:
    """dbc.Card containing link buttons to sensor dashboards."""

    button_style = {'color': 'info'}
    children = [
        templates.card_header('Sensors', 'tower-broadcast'),
        dbc.Stack(
            [
                html.Div(
                    id='card-sensors-status-text'
                ),
                dbc.Container(
                    [
                        dbc.Button(
                            ['View', html.Br(), 'Sensors'],
                            **button_style,
                            href='/sensors'
                        ),
                        dbc.Button(
                            ['View Data Connectors', html.Br(), 'and Gateways'],
                            **button_style,
                            href='/gateway-data-connectors'
                        ),
                        dbc.Button(
                            [
                                "2D Map",
                                html.Br(),
                                html.Span(className='fa fa-map-location-dot')
                            ],
                            **button_style,
                            href='/sensors/2d'
                        )
                    ],
                    class_name='d-flex gap-2'
                )
            ],
            className='gap-2 card-text'
        )
    ]

    return dbc.CardBody(
        children=children,
    )


def card_hpath() -> dbc.Card:
    """dbc.Card containing link to histopathology dashboards."""

    cardbutton_style = {'color': 'info',  'class_name': 'card-text', 'style': {'width': '300px'}}
    cardbutton_title_style = {'style': {'font-size': '1.0rem'}}
    cardbutton_text_style = {'style': {'font-size': '0.7rem', 'text-align': 'justify'}}

    children = [
        templates.card_header('Histopathology', 'bacteria', color='#a09'),
        dbc.Stack(
            [
                dbc.Button(
                    [
                        html.Div(
                            [
                                html.Span(className="fa fa-microchip"),
                                '\u2002Simulator'  # en space
                            ],
                            **cardbutton_title_style
                        ),
                        html.Div(
                            'Simulation model of Addenbrooke\'s  Hospital\'s Histopathology '
                            'department. Visualise KPIs online, or download an report in JSON '
                            'format.',
                            **cardbutton_text_style
                        )
                    ],
                    id='homepage-button-hpath',
                    href='/hpath',
                    **cardbutton_style
                ),
                dbc.Button(
                    [
                        html.Div(
                            [
                                html.Span(className="fa fa-diagram-project"),
                                '\u2002Building Information Management (BIM) Model'  # en space
                            ],
                            **cardbutton_title_style
                        ),
                        html.Div(
                            ['Set path availability and compute travel times. '
                             'The exported Excel sheet can be inserted into a '
                             'configuration file for the Simulator.\u2002', html.B('(TODO)')],
                            **cardbutton_text_style
                        )
                    ],
                    id='homepage-button-hpath',
                    href='/hpath/bim',
                    **cardbutton_style
                ),
            ],
            class_name='gap-2 card-text'
        )
    ]

    return dbc.CardBody(children=children)


def card_status() -> dbc.Card:
    """dbc.Card for showing server status."""

    status_style = {'style': {'font-size': '0.9rem'}}
    children = [
        templates.card_header('Server status', 'heart-pulse', color='#c00'),
        html.Div(
            [
                html.Span('❓ ', className='emoji', id='homepage-status-bullet-sensors'),
                'Sensor server'
            ],
            **status_style

        ),
        html.Div(
            [
                html.Span('❓ ', className='emoji', id='homepage-status-bullet-hpath'),
                'Histopathology simulation server'
            ],
            **status_style
        ),
        dcc.Interval(id='check-status', interval=5000)
    ]
    return dbc.CardBody(
        children=children
    )

#####################################################################
##                                                                 ##
##    ##          ###    ##    ##  #######  ##     ## ########     ##
##    ##         ## ##    ##  ##  ##     ## ##     ##    ##        ##
##    ##        ##   ##    ####   ##     ## ##     ##    ##        ##
##    ##       ##     ##    ##    ##     ## ##     ##    ##        ##
##    ##       #########    ##    ##     ## ##     ##    ##        ##
##    ##       ##     ##    ##    ##     ## ##     ##    ##        ##
##    ######## ##     ##    ##     #######   #######     ##        ##
##                                                                 ##
#####################################################################


auto_col_style = {'width': 'auto', 'class_name': 'p-0'}

layout = dbc.Stack(
    [
        dbc.Breadcrumb(
            items=[
                {'label': 'Home', 'active': True},
            ],
            class_name='mx-0'
        ),
        templates.page_title('CUH Digital Hospitals Dashboards Demo'),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card([card_sensors()], style={'height': '100%'}),
                    **auto_col_style
                ),
                dbc.Col(
                    dbc.Card([card_hpath()], style={'height': '100%'}),
                    **auto_col_style
                ),
                dbc.Col(
                    dbc.Card([card_status()], style={'height': '100%'}),
                    **auto_col_style
                )
            ],
            class_name='d-flex gap-3 mx-0'
        )
    ]
)

###############################################################################################
##                                                                                            ##
##     ######     ###    ##       ##       ########     ###     ######  ##    ##  ######      ##
##    ##    ##   ## ##   ##       ##       ##     ##   ## ##   ##    ## ##   ##  ##    ##     ##
##    ##        ##   ##  ##       ##       ##     ##  ##   ##  ##       ##  ##   ##           ##
##    ##       ##     ## ##       ##       ########  ##     ## ##       #####     ######      ##
##    ##       ######### ##       ##       ##     ## ######### ##       ##  ##         ##     ##
##    ##    ## ##     ## ##       ##       ##     ## ##     ## ##    ## ##   ##  ##    ##     ##
##     ######  ##     ## ######## ######## ########  ##     ##  ######  ##    ##  ######      ##
##                                                                                            ##
################################################################################################


@callback(
    Output('homepage-status-bullet-sensors', 'children'),
    Output('homepage-status-bullet-hpath', 'children'),
    Input('check-status', 'n_intervals'),
    # prevent_initial_call=True
)
def status_bullet_colors(_) -> tuple[Component, Component]:
    """Update the server status messages on the home page. Triggered
    by a dcc.Interval component."""
    try:
        REDIS_CONN.ping()
        redis_ok = True
    except RedisError:
        redis_ok = False

    try:
        response = requests.get(SENSOR_HOST, timeout=5)
        sensor_ok = response.status_code == 200
    except requests.RequestException:
        sensor_ok = False

    logger = logging.getLogger('dash.dash')
    logger.info("ping sensor-server: %s", 'OK' if sensor_ok else 'FAIL')
    logger.info("ping redis: %s", 'OK' if redis_ok else 'FAIL')

    return (
        '✔ ' if sensor_ok else '❌ ',
        '✔ ' if redis_ok else '❌ '
    )
