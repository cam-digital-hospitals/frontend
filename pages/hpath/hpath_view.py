"""Menu page for choosing between the single-scenario and multi-scenario result menus."""
import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash_compose import composition

from pages import templates

dash.register_page(__name__, title='Histopathology: Results', icon='house-fill', path='/hpath/view')

auto_col_style = {'width': 'auto', 'class_name': 'p-0'}
card_style = {'inverse': True, 'class_name': 'p-3'}


@composition
def layout():
    """Page layout."""
    with dbc.Stack() as ret:
        yield templates.breadcrumb(
            ['Home', 'Histopathology: Simulator', 'View Simulation Results'],
            ['hpath', 'view']
        )
        yield templates.page_title('Histopathology: View Simulation Results')
        with dbc.Row(class_name='d-flex gap-3 mx-0'):
            with dbc.Col(**auto_col_style):
                with dcc.Link(style={'text-decoration': 'none'}, href='/hpath/view/single'):
                    with dbc.Card(color='info', **card_style):
                        with dbc.CardBody():
                            yield templates.card_header('Single-Scenario Analysis', 'file')
            with dbc.Col(**auto_col_style):
                with dcc.Link(style={'text-decoration': 'none'}, href='/hpath/view/multi'):
                    with dbc.Card(color='info', **card_style):
                        with dbc.CardBody():
                            yield templates.card_header('Multiple-Scenario Analysis', 'folder-open')
    return ret
