"""Menu page for selecting single scenarios to view results."""
from datetime import datetime
from http import HTTPStatus
import logging
from math import isnan
import dash
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from dash_compose import composition
import pandas as pd
from dash import Input, Output, callback, html
import pytz
import requests

from conf import HPATH_RESTFUL_HOST
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

# See: https://dash.plotly.com/dash-ag-grid/cell-renderer-components

sc_grid_coldefs = [
    {'field': 'scenario_id', 'headerName': '#', 'width': '80px', 'sortable': True, 'sort': 'asc'},
    {'field': 'scenario_name', 'headerName': 'Scenario Name', 'sortable': True, 'width': '160px'},
    {'field': 'analysis_id', 'headerName': 'Analysis #', 'width': '100px'},
    {'field': 'analysis_name', 'headerName': 'Analysis Name', 'sortable': True, 'width': '140px'},
    {'field': 'created', 'headerName': 'Created', 'width': '220px'},
    {'field': 'completed', 'headerName': 'Completed', 'width': '220px'},
    {'field': 'progress', 'headerName': 'Progress', 'width': '100px'},
    {
        'field': 'result_link',
        'headerName': 'Results',
        'width': '100px',
        # resultLink function is defined in the dashAgGridComponentFunctions.js in assets folder
        "cellRenderer": "resultLinkScenario",
    }
]
"""Defines column settings for the AG Grid object on this page."""

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
def btn_refresh():
    """Refresh button for updating scenario statuses.
    """
    with dbc.Row() as ret:
        with dbc.Col(style=auto_col_style):
            yield dbc.Button(
                ['Refresh\u2002', html.Span(className='fa fa-arrows-rotate')],
                id='btn-scenarios-refresh',
                color='info',
                class_name='mb-3',
                style={'width': 'auto'}
            )
    return ret


@composition
def layout():
    """Page layout."""
    with dbc.Stack() as ret:
        yield templates.breadcrumb(
            [
                'Home',
                'Histopathology: Simulator',
                'View Simulation Results',
                'Single-Scenario Results'
            ],
            ['hpath', 'view', 'single']
        )
        yield templates.page_title('Histopathology: Single-Scenario Results')
        yield btn_refresh()
        yield dag.AgGrid(
            id='hpath-view-scenarios',
            rowData=sc_df_init.to_dict('records'),
            columnDefs=sc_grid_coldefs
        )
    return ret

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
    """Format a UNIX timestamp in the format 2023-11-11 11:11:11 GMT (or BST for summer time)."""
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
            url=f'{HPATH_RESTFUL_HOST}/scenarios/',
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
        # TODO: display error messages on screen
        return sc_df_init
