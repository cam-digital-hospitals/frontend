"""Page for submitting simulation jobs."""
import logging
from base64 import b64decode
from http import HTTPStatus

import dash
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from dash_compose import composition
import humanize
import pandas as pd
import requests
from dash import Input, Output, State, callback, dcc, html

from conf import HPATH_RESTFUL_HOST
from pages import templates

dash.register_page(__name__, title='Histopathology: Submit Scenarios', path='/hpath/submit')

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
    'file_name': [],
    'sc_name': [],
    'file_base64': [],
    'decode_len_str': []
})
"""Defines an empty scenarios dataframe. Required because some representations of
an empty dataframe cannot hold column metadata."""

sc_grid_coldefs = [
    {
        'field': 'controls',
        'headerName': '',
        'checkboxSelection': True,
        "headerCheckboxSelection": True,
        'width': '40px'
    },
    {
        'field': 'file_name',
        'headerName': 'File name',
    },
    {
        'field': 'sc_name',
        'headerName': 'Scenario name',
        'editable': True,

        # Force ascending order sort
        'sortable': True,
        'sortingOrder': ['asc'],
        'sort': 'asc',
    },
    {
        'field': 'decode_len_str',
        'headerName': 'File length'
    }
]
"""Defines column settings for the AG Grid object on this page.  See also
``sc_grid_default_coldefs`` for default column settings."""

sc_grid_default_coldefs = {
    "resizable": True,
    'sortable': False
}
"""Defines default column settings for the AG Grid object on this page.  See also
``sc_grid_coldefs`` for overrriden column settings."""

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

unit_selector = dbc.Select(
    options=["Weeks", "Days", "Hours"],
    value="Weeks",
    id='hpath-submitter-sim-length-units',
    style={'width': '100px', 'max-width': '100px'},
    class_name='m-0'
)
"""Input for selecting the unit of the inputted simulation length (weeks, days, or hours)."""

analysis_name_input: dbc.Col = templates.labelled_input(
    'Analysis name',
    id='hpath-submitter-analysis-name',
    disabled=True,
    prompt='Enter a name.'
)
"""Input with label (as a dbc.Col) for inputting an analysis name."""

sim_length_inputs: dbc.Col = templates.labelled_numeric(
    'Simulation length',
    id='hpath-submitter-sim-length',
    init=4,
    unit_selector=unit_selector
)
"""Input group selecting the unit of the inputted simulation length."""

@composition
def layout():
    """Page layout."""
    with dbc.Stack() as ret:
        yield templates.breadcrumb(
            ['Home', 'Histopathology: Simulator', 'Submit Simulation Job'],
            ['hpath', 'submit']
        )
        yield templates.page_title('Histopathology: Submit Simulation Job(s)')
        with dbc.Card(class_name='p-3'):
            yield templates.card_header('Upload scenario configuration file(s)', 'upload')

            # Row for alert messages
            with dbc.Row(class_name='mx-0 mt-1'):
                with dbc.Col(class_name='m-0 p-0', width=12):
                    yield dbc.Alert(
                        id='hpath-submitter-alert',
                        color='secondary',
                        dismissable=True,
                        is_open=False,
                        class_name='m-0'
                    )

            # Row with Upload and Download Template buttons
            with dbc.Row(class_name='mx-0 mt-3 g-2'):

                # Upload file(s)
                with dbc.Col(class_name='m-0', width="auto"):
                    with dcc.Upload(
                        id='hpath-submitter-upload-files',
                        accept='.xlsx',
                        multiple=True,
                        className='m-0'
                    ):
                        with dbc.Button(
                            id='hpath-submitter-btn-select-files', class_name='m-0'
                        ):
                            yield html.Span(className='fa fa-upload')
                            yield '\u2002Upload file(s)'

                # Download Template file
                with dbc.Col(class_name='m-0', width="auto"):
                    with dbc.Button(
                        id='hpath-download-template-btn', class_name='m-0'
                    ):
                        yield html.Span(className='fa fa-download')
                        yield '\u2002Download template file'
                    yield dcc.Download(id='hpath-download-file')

            # Row with info regarding multi-scenario analyses
            with dbc.Row(class_name='mx-0 mt-3'):
                with dbc.Col(width='auto'):
                    yield 'If multiple files are uploaded, a '
                    yield html.B('multi-scenario analysis ')
                    yield 'will be created. Enter an analysis name below '\
                        '(disabled for single-scenario analyses).'

            # Row for setting Analysis name and simulation lengths
            with dbc.Row(align="start", justify="start", className='mx-0 mt-1 g-4'):
                yield analysis_name_input
                yield sim_length_inputs

            # Row with info on using the AG Grid element
            with dbc.Row(class_name='mx-0 mt-3'):
                with dbc.Col(width='auto'):
                    yield 'The scenario names defined in the table below will be used to '\
                        'retrieve simulation results. Double-click on a scenario name to '\
                        'edit it.  Scenarios appear in the multi-scenario report in '
                    with html.Span(style={'color': 'red', 'font-weight': 'bold'}):
                        yield 'alphanumerical order '
                    yield html.Br()
                    yield 'Default scenario names are provided based on the uploaded filenames, '\
                        'with “ copy” appended in event of a name clash.'

            # Scenarios AG Grid
            with dbc.Row(class_name='mx-0 mt-1'):
                with dbc.Col(width=12):
                    yield dag.AgGrid(
                        id='hpath-submitter-grid',
                        rowData=sc_df_init.to_dict('records'),
                        columnDefs=sc_grid_coldefs,
                        defaultColDef=sc_grid_default_coldefs,
                        dashGridOptions={
                            "singleClickEdit": True,
                            "enterMovesDown": True,
                            "enterMovesDownAfterEdit": True,
                            "stopEditingWhenCellsLoseFocus": True,
                            'rowSelection': 'multiple'
                        }
                    )

            # Row with Delete and Submit buttions
            with dbc.Row(class_name='mx-0 mt-3 g-2'):
                with dbc.Col(width='auto', class_name='m-0'):
                    yield dbc.Button(
                        'Delete selected rows',
                        id='hpath-submitter-delete-btn',
                        color='danger'
                    )
                with dbc.Col(width='auto', class_name='m-0'):
                    yield dbc.Button(
                        'Submit',
                        id='hpath-submitter-submit-btn',
                        disabled=True,
                        color='secondary'
                    )

        # Modal for Submit callback results
        #yield submit_msg_modal
        with dbc.Modal(
            id='hpath-submitter-modal',
            is_open=False,
            backdrop='static',
            size='xl',
            fullscreen='lg-down'
        ):
            yield dbc.ModalHeader()
            with dbc.ModalBody(
                id='hpath-submitter-modal-body',
                class_name='py-0'
            ):
                yield 'This is a modal dialog'
            with dbc.ModalFooter():
                with dbc.Button(
                    id='hpath-submitter-view-results-btn',
                    className="ms-auto",
                    href='/hpath/view'
                ):
                    yield 'View Results'
                with dbc.Button(id="hpath-submitter-modal-close", n_clicks=0):
                    yield 'Close'

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


@callback(
    Output('hpath-download-file', 'data'),
    Input('hpath-download-template-btn', 'n_clicks'),
    prevent_initial_call=True
)
def download_hpath_template(_):
    """Triggered when the "Download template file" button is pressed."""
    # actual filesystem, no need for get_asset_url
    return dcc.send_file('static/examples/config.xlsx')


@callback(
    Output('hpath-submitter-grid', 'deleteSelectedRows'),
    Input('hpath-submitter-delete-btn', 'n_clicks'),
    prevent_initial_call=True,
)
def hpath_submitter_delete_rows(_):
    """Triggered when the "Delete selected rows" button is pressed."""
    return True


@callback(
    Output('hpath-submitter-analysis-name', 'disabled'),
    Output('hpath-submitter-submit-btn', 'disabled'),
    Output('hpath-submitter-submit-btn', 'color'),
    Input('hpath-submitter-grid', 'rowData'),
    Input('hpath-submitter-analysis-name', 'value'),
    Input('hpath-submitter-sim-length', 'value')
)
def input_states(row_data, name_value, sim_length_value):
    """Checks if all inputs are valid and enables/disables the submit button
    accordingly.  Also enables/disables the analysis name input for
    single-scenario analyses."""

    name_df = sc_df_init if row_data == [] else pd.DataFrame(row_data)
    empty = len(name_df) == 0
    multi = len(name_df) > 1
    missing_analysis_name = multi and (name_value == '' or name_value is None)
    try:
        can_submit = (not empty
                      and not missing_analysis_name
                      and float(sim_length_value) > 0
                      )
    except ValueError:  # Catch invalid simulation length
        can_submit = False

    return (
        len(name_df) < 2,
        missing_analysis_name,
        'success' if can_submit else 'secondary'
    )


@callback(
    Output('hpath-submitter-alert', 'children'),
    Output('hpath-submitter-alert', 'color'),
    Output('hpath-submitter-alert', 'is_open'),
    Output('hpath-submitter-upload-files', 'contents'),
    Output('hpath-submitter-grid', 'rowData'),

    Input('hpath-submitter-upload-files', 'contents'),
    Input('hpath-submitter-grid', 'cellValueChanged'),
    State('hpath-submitter-upload-files', 'filename'),
    State('hpath-submitter-grid', 'rowData'),
    prevent_inital_call=True
)
def manage_grid_data(contents, _, names, old_sc_data: dict):
    """Manages file uploads and changes to scenario names
    by updating the AG Grid data (name changes force re-sort)."""

    sc_df = sc_df_init if old_sc_data == [] else pd.DataFrame(old_sc_data)

    # Check uploaded file data only if upload Component was triggered
    if dash.ctx.triggered_id == 'hpath-submitter-upload-files':
        if contents is None:
            return (
                dash.no_update,
                dash.no_update,
                dash.no_update,
                None,
                dash.no_update
            )

        n_new_files = 0
        for file_name, content in zip(names, contents):
            sc_name = file_name.rsplit('.xlsx', 1)[0]
            while sc_name in sc_df.sc_name.to_list():
                sc_name = f'{sc_name} copy'

            # update pandas DataTable (name, scenario name)
            b64string = content.split('base64,')[1]
            # print(file_name, sc_name, len(b64string), b64string[-8:])
            new_row = pd.DataFrame({
                'file_name': [file_name],
                'sc_name': [sc_name],
                'file_base64': content,
                'decode_len_str': humanize.naturalsize(len(b64decode(b64string)))
            })
            sc_df: pd.DataFrame = pd.concat([sc_df, new_row], axis='rows', ignore_index=True)
            n_new_files += 1

    # Sort the scenarios by name (for both new file upload and scenario rename)
    sc_df = sc_df.sort_values('sc_name', ignore_index=True)
    sc_data = sc_df.to_dict('records')

    if dash.ctx.triggered_id == 'hpath-submitter-upload-files':
        return (
            [
                html.Span(className='fa fa-circle-check'),
                f'\u2002Successfully uploaded {n_new_files} file(s).'
            ],
            'success',
            True,
            None,
            sc_data
        )
    return (
        dash.no_update,
        dash.no_update,
        dash.no_update,
        None,
        sc_data
    )


@callback(
    Output('hpath-submitter-modal', 'is_open'),
    Output('hpath-submitter-modal-body', 'children'),     # Modal message
    Output('hpath-submitter-view-results-btn', 'style'),  # Show/hide "View Results" button
    Input('hpath-submitter-submit-btn', 'n_clicks'),
    State('hpath-submitter-grid', 'rowData'),
    State('hpath-submitter-analysis-name', 'value'),
    State('hpath-submitter-sim-length', 'value'),
    State('hpath-submitter-sim-length-units', 'value'),
    prevent_initial_call=True
)
def submit_or_close_modal(_, sc_data, analysis_name, sim_length, sim_length_unit):
    """Process a simulation job request when the Submit button is pressed."""

    logger = logging.getLogger('dash.dash')

    logger.info('SUBMIT')
    if len(sc_data) > 1:
        logger.info("Analysis name: %s", analysis_name)

    # sim_length and sim_length_unit should already be validated by Dash input constraints
    sim_length_unit_factor = (
        168 if sim_length_unit == "Weeks"
        else 24 if sim_length_unit == "Days"
        else 1
    )

    # parameters common to all submitted scenarios
    params = {
        'sim_hours': sim_length * sim_length_unit_factor,
        'num_reps': 1,
        'analysis_name': analysis_name
    }
    logger.info(params)

    try:
        response = requests.post(
            url=f'{HPATH_RESTFUL_HOST}/submit/',
            json={
                'params': params,
                'scenarios': sc_data
            },
            timeout=10
        )
    except requests.exceptions.Timeout:
        logger.error('Request timed out.')
        return (
            True,
            html.Div("Request timed out.", className='m-0', style={'color': 'crimson'}),
            {'display': 'none'}
        )
    except requests.exceptions.RequestException as exc:
        logger.error("Request exception raised (type %s): %s", str(type(exc)), str(exc))
        error_msg = [html.P(f"Request exception raised (type {type(exc)}): "), html.Pre(str(exc))]
        return (
            True,
            html.Div(error_msg, className='m-0', style={'color': 'crimson'}),
            {'display': 'none'}
        )

    if response.status_code == HTTPStatus.OK:
        logger.info('OK!')
        return (
            True,
            f"Sucessfully created {'single' if len(sc_data) == 1 else 'multi'}-scenario analysis!",
            None
        )

    # else: error
    logger.error("Error message received from backend server (type %s): ", response.json()['type'])
    logger.error(response.json()['msg'])
    error_msg = [
        html.P(
            f"Error message received from backend server (type {response.json()['type']}): "
        ),
        html.Pre(response.json()['msg'])
    ]
    return (
        True,
        html.Div(error_msg, className='m-0', style={'color': 'crimson'}),
        {'display': 'none'}
    )


@callback(
    Output('hpath-submitter-modal', 'is_open', allow_duplicate=True),
    Input('hpath-submitter-modal-close', 'n_clicks'),
    prevent_initial_call=True
)
def close_modal(_):
    """Closes the modal dialog for submission-related messages."""
    return False
