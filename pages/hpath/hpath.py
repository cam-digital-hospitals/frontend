"""Menu page for the Histopathology Simulator."""
from http import HTTPStatus
import logging

import dash
import dash_bootstrap_components as dbc
from dash import html, callback, Input, Output
from dash_compose import composition
import requests

from pages import templates
from conf import HPATH_RESTFUL_HOST

dash.register_page(__name__, title='Histopathology', path='/hpath')


btn_style = {'color': 'info', 'style': {'height': '100%'}}
red_btn_style = {'color': 'danger', 'style': {'height': '100%'}}
auto_col_style = {'width': 'auto', 'class_name': 'p-0'}
hidden = {'display': 'none'}

CLEAR_DB_CONFIRMATION_MSG = 'Clear simulation results database? Click anywhere '\
    'outside this dialog box to cancel.'

btn_submit_page = dbc.Button(
    [
        templates.card_header(
            'Submit Simulation Job',
            'square-caret-right',
            regular=True,
            pad_below=False
        )
    ],
    href='/hpath/submit',
    **btn_style
)

btn_view_page = dbc.Button(
    [templates.card_header('View Results', 'search', pad_below=False)],
    href='/hpath/view',
    **btn_style
)

btn_clear_db = dbc.Button(
    [templates.card_header('Clear database', 'trash-can', pad_below=False)],
    id='clear-db',
    href='#',
    **red_btn_style
)


@composition
def layout():
    """Page layout."""
    with dbc.Stack() as ret:
        yield templates.breadcrumb(['Home', 'Histopathology: Simulator'], ['hpath'])
        yield templates.page_title('Histopathology: Simulator')
        with dbc.Row(class_name='d-flex gap-3 mx-0 mt-3'):
            with dbc.Col(**auto_col_style):
                yield btn_submit_page
            with dbc.Col(**auto_col_style):
                yield btn_view_page
            with dbc.Col(**auto_col_style):
                yield btn_clear_db
        with dbc.Modal(id='clear-db-modal', is_open=False):
            with dbc.ModalHeader(id='clear-db-modal-header', close_button=False):
                yield dbc.ModalTitle('Danger!')
            with dbc.ModalBody(id='clear-db-modal-msg'):
                yield CLEAR_DB_CONFIRMATION_MSG
            with dbc.ModalFooter():
                with dbc.Button(id='clear-db-modal-cancel', color='primary', style={}):
                    yield 'Cancel'
                with dbc.Button(id='clear-db-modal-yes', color='danger', style={}):
                    yield 'Delete!'
                with dbc.Button(id='clear-db-modal-close', color='primary', style={}):
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
    Output('clear-db-modal', 'is_open'),
    Output('clear-db-modal-header', 'children'),
    Output('clear-db-modal-msg', 'children'),
    Output('clear-db-modal-cancel', 'style'),
    Output('clear-db-modal-yes', 'style'),
    Output('clear-db-modal-close', 'style'),
    Input('clear-db', 'n_clicks'),
    Input('clear-db-modal-cancel', 'n_clicks'),
    Input('clear-db-modal-yes', 'n_clicks'),
    Input('clear-db-modal-close', 'n_clicks'),
    prevent_initial_call=True
)
def clear_db_confirmation(*_):
    """Handle callbacks for clearing the database."""

    logger = logging.getLogger('dash.dash')
    logger.info(dash.ctx.triggered_id)

    # Clear database button (the BIG RED button!)
    if dash.ctx.triggered_id == 'clear-db':
        return True, dbc.ModalTitle('Danger!'), CLEAR_DB_CONFIRMATION_MSG, {}, {}, hidden

    # Cancel or Close buttons
    if dash.ctx.triggered_id in ['clear-db-modal-cancel', 'clear-db-modal-close']:
        return False, [], [], hidden, hidden, hidden

    # Confirmation button (Small 'Delete!' button)
    if dash.ctx.triggered_id == 'clear-db-modal-yes':
        try:
            response = requests.delete(
                url=f'{HPATH_RESTFUL_HOST}/',
                json={'delete': 'yes'},
                timeout=10
            )
            assert response.status_code == HTTPStatus.OK
            return True, [], 'Database cleared!', hidden, hidden, {}
        except AssertionError:
            error_msg = [
                html.B("Non-200 (OK) HTTP response received: "),
                f"{response.status_code} {HTTPStatus(response.status_code).name}"
            ]

            return True, dbc.ModalTitle('Error!'), error_msg, hidden, hidden, {}
        except requests.exceptions.RequestException as exc:
            error_msg = f"An error occured (type {type(exc)})."
            error_pre = html.Pre(f"{error_msg}\n\n{str(exc)}")
            return True, dbc.ModalTitle('Error!'), error_pre, hidden, hidden, {}

    # None of the above: hide modal
    return False, [], [], hidden, hidden, hidden
