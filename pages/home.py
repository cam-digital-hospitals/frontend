"""Content of the home page, with buttons to various parts of the webapp."""
import logging

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dcc, html
from dash.development.base_component import Component
from dash_compose import composition
from redis import Redis
from redis.exceptions import RedisError
import requests

from conf import REDIS_HOST, REDIS_PORT, SENSOR_HOST, HPATH_RESTFUL_HOST
from pages import templates

REDIS_CONN = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT  # default
)
"""Provides an connection to the redis server at ``redis://<REDIS_HOST>:<REDIS_PORT>``."""

dash.register_page(__name__, title='Homepage', path='/')

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


@composition
def page_layout():
    """The page layout, to be inserted into the multi-page Dash app."""
    with dbc.Stack() as stack:
        yield dbc.Breadcrumb(
            items=[
                {'label': 'Home', 'active': True},
            ],
            class_name='mx-0'
        )
        yield templates.page_title('CUH Digital Hospitals Dashboards Demo')
        with dbc.Row(class_name='d-flex gap-3 mx-0'):

            # SENSORS
            with dbc.Col(**auto_col_style):
                with dbc.Card(style={'height': '100%'}):
                    button_style = {'color': 'info'}

                    with dbc.CardBody():
                        yield templates.card_header('Sensors', 'tower-broadcast')
                        with dbc.Stack(className='gap-2 card-text'):
                            with dbc.Container(class_name='d-flex gap-2'):
                                yield dbc.Button(
                                    ['View', html.Br(), 'Sensors'],
                                    **button_style,
                                    href='/sensors'
                                )
                                yield dbc.Button(
                                    ['View Data Connectors', html.Br(), 'and Gateways'],
                                    **button_style,
                                    href='/gateway-data-connectors'
                                )
                                yield dbc.Button(
                                    [
                                        "2D Map",
                                        html.Br(),
                                        html.Span(className='fa fa-map-location-dot')
                                    ],
                                    **button_style,
                                    href='/sensors/2d'
                                )

            # HISTOPATHOLOGY SIMULATION MODEL
            with dbc.Col(**auto_col_style):
                with dbc.Card(style={'height': '100%'}):
                    button_style = {
                        'color': 'info',
                        'class_name': 'card-text',
                        'style': {'width': '300px'}
                    }
                    button_title_style = {'style': {'font-size': '1.0rem'}}
                    button_text_style = {
                        'style': {'font-size': '0.7rem', 'text-align': 'justify'}
                    }

                    with dbc.CardBody():
                        yield templates.card_header('Histopathology', 'bacteria', color='#a09')
                        with dbc.Stack(className='gap-2 card-text'):
                            with dbc.Button(
                                id='homepage-button-hpath',
                                href='/hpath',
                                **button_style
                            ):
                                with html.Div(**button_title_style):
                                    yield html.Span(className="fa fa-microchip")
                                    yield '\u2002Simulator'  # en space
                                with html.Div(**button_text_style):
                                    yield (
                                        'Simulation model of Addenbrooke\'s  Hospital\'s '
                                        'Histopathology  department. Visualise KPIs online, or '
                                        'download an report in JSON format.'
                                    )

                            with dbc.Button(
                                id='homepage-button-hpath',
                                href='/hpath/bim',
                                **button_style
                            ):
                                with html.Div(**button_title_style):
                                    yield html.Span(className="fa fa-diagram-project")
                                    yield '\u2002Building Information Management (BIM) Model'
                                with html.Div(**button_text_style):
                                    yield (
                                        'Set path availability and compute travel times. '
                                        'The exported Excel sheet can be inserted into a '
                                        'configuration file for the Simulator.\u2002'
                                    )

            # SERVER STATUS
            with dbc.Col(**auto_col_style):
                with dbc.Card(style={'height': '100%'}):
                    status_style = {'style': {'font-size': '0.9rem'}}

                    with dbc.CardBody():
                        yield templates.card_header('Server status', 'heart-pulse', color='#c00')
                        with html.Div(**status_style):
                            yield html.Span(
                                '❓ ', className='emoji', id='homepage-status-bullet-sensors'
                            )
                            yield 'Sensor server'
                        with html.Div(**status_style):
                            yield html.Span(
                                '❓ ', className='emoji', id='homepage-status-bullet-hpath'
                            )
                            yield 'Histopathology simulation server'
            yield dcc.Interval(id='check-status', interval=5000)

    return stack


layout = page_layout()

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
    
    # NOTE: timeout interval must be shorter than the dcc.Interval's interval
    # or else the React element won't update before the next callback

    try:
        response = requests.get(HPATH_RESTFUL_HOST, timeout=2)
        hpath_rest_ok = response.status_code == 200
    except requests.RequestException:
        hpath_rest_ok = False

    try:
        response = requests.get(SENSOR_HOST, timeout=2)
        sensor_ok = response.status_code == 200
    except requests.RequestException:
        sensor_ok = False

    logger = logging.getLogger('dash.dash')
    logger.info("ping sensor-server: %s", 'OK' if sensor_ok else 'FAIL')
    logger.info("ping redis: %s", 'OK' if redis_ok else 'FAIL')
    logger.info("ping hpath-rest: %s", 'OK' if hpath_rest_ok else 'FAIL')

    return (
        '✔ ' if sensor_ok else '❌ ',
        '✔ ' if (redis_ok and hpath_rest_ok) else '❌ '
    )
