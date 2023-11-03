"""Menu page for selecting single scenarios to view results."""
from datetime import datetime
from http import HTTPStatus
import logging
from math import isnan
import dash
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, callback, html
import pytz
import requests

from dash_app.conf import HPATH_SIM_HOST, HPATH_SIM_PORT
from pages import templates

dash.register_page(
    __name__,
    title='Histopathology: List Scenarios',
    path='/hpath/view/single'
)

#####################################################################
##       ###     ######       ######   ########  #### ########     ##
##      ## ##   ##    ##     ##    ##  ##     ##  ##  ##     ##    ##
##     ##   ##  ##           ##        ##     ##  ##  ##     ##    ##
##    ##     ## ##   ####    ##   #### ########   ##  ##     ##    ##
##    ######### ##    ##     ##    ##  ##   ##    ##  ##     ##    ##
##    ##     ## ##    ##     ##    ##  ##    ##   ##  ##     ##    ##
##    ##     ##  ######       ######   ##     ## #### ########     ##
#####################################################################

sc_df_init = pd.DataFrame({
    'scenario_id': [],
    'scenario_name': [],
    'analysis_id': [],
    'analysis_name': [],
    'created': [],
    'completed': [],
    'progress': [],
    'results': [],
    'file_name': [],
    'file_base64': [],
    'decode_len_str': []
})
"""Defines an empty scenarios dataframe. Required because some representations of
an empty dataframe cannot hold column metadata."""

# TODO: add "Results" and "Config File" columns
# See: https://dash.plotly.com/dash-ag-grid/cell-renderer-components

sc_grid_coldefs = [
    {'field': 'scenario_id', 'headerName': '#', 'width': '80px'},
    {'field': 'scenario_name', 'headerName': 'Scenario Name', 'width': '160px'},
    {'field': 'analysis_id', 'headerName': 'Analysis #', 'width': '120px'},
    {'field': 'analysis_name', 'headerName': 'Analysis Name', 'width': '160px'},
    {'field': 'created', 'headerName': 'Created', 'width': '240px'},
    {'field': 'completed', 'headerName': 'Completed', 'width': '240px'},
    {'field': 'progress', 'headerName': 'Progress', 'width': '160px'},
    {
        'field': 'result_link',
        'headerName': 'Results',
        'width': '160px',
        # resultLink function is defined in the dashAgGridComponentFunctions.js in assets folder
        "cellRenderer": "resultLinkScenario",
    }
]
"""Defines column settings for the AG Grid object on this page.  See also
``sc_naming_default_coldefs`` for default column settings."""

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

btn_refresh = dbc.Row(
    dbc.Col(
        dbc.Button(
            ['Refresh\u2002', html.Span(className='fa fa-arrows-rotate')],
            id='btn-scenarios-refresh',
            color='info',
            class_name='mb-3',
            style={'width': 'auto'}
        ),
        style=auto_col_style)
)

layout = dbc.Stack(
    [
        templates.breadcrumb(
            [
                'Home',
                'Histopathology: Simulator',
                'View Simulation Results',
                'Single-Scenario Results'
            ],
            ['hpath', 'view', 'single']
        ),
        templates.page_title('Histopathology: Single-Scenario Results'),
        btn_refresh,
        dag.AgGrid(
            id='hpath-view-scenarios',
            rowData=sc_df_init.to_dict('records'),
            columnDefs=sc_grid_coldefs
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


LONDON = pytz.timezone('Europe/London')

def format_time(ts: float):
    return datetime.utcfromtimestamp(ts).astimezone(LONDON).strftime('%Y-%m-%d %H:%M:%S %Z')


@callback(
    Output('hpath-view-scenarios', 'rowData'),
    Input('btn-scenarios-refresh', 'n_clicks')
)
def load_scenarios(n_clicks) -> None:
    """Load or refresh the scenarios list."""
    logger = logging.getLogger('dash.dash')
    logger.info('load_scenarios: %s', n_clicks)

    try:
        response = requests.get(
            url=f'http://{HPATH_SIM_HOST}:{HPATH_SIM_PORT}/scenarios/',
            timeout=10
        )
        assert response.status_code == HTTPStatus.OK
        scenarios = response.json()

        for val in scenarios:
            completed = isinstance(val['completed'], float) and not isnan(val['completed'])
            if isinstance(val['created'], float) and not isnan(val['created']):
                val['created'] = format_time(val['created'])
            if completed:
                val['completed'] = format_time(val['completed'])
            val['progress'] = f"{val['done_reps']}/{val['num_reps']}"
            val['result_link'] = f"{val['scenario_id']}" if completed else ''
        logger.info(scenarios)
        return scenarios
    except:
        # TODO: display error message on screen
        return sc_df_init
