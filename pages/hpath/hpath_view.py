"""Menu page for choosing between the single-scenario and multi-scenario result menus."""
import dash
import dash_bootstrap_components as dbc
from dash import dcc

from pages import templates

dash.register_page(__name__, title='Histopathology: Results', icon='house-fill', path='/hpath/view')


layout = dbc.Stack(
    [
        templates.breadcrumb(
            ['Home', 'Histopathology: Simulator', 'View Simulation Results'],
            ['hpath', 'view']
        ),
        templates.page_title('Histopathology: View Simulation Results'),
        dbc.Stack(
            [
                dcc.Link(
                    dbc.Card(
                        [
                            templates.card_header('Single-Scenario Analysis', 'file-earmark'),
                            'Detailed statistics for a single simulation scenario.'
                        ],
                        color='info',
                        inverse=True,
                        class_name='p-3'
                    ),
                    style={'text-decoration': 'none'},
                    href='/hpath/view/single'
                ),
                dcc.Link(
                    dbc.Card(
                        [
                            templates.card_header('Multiple-Scenario Analysis', 'folder-fill'),
                            'Summary statistics for a group of related simulation scenarios.'
                        ],
                        color='info',
                        inverse=True,
                        class_name='p-3 mt-3'
                    ),
                    style={'text-decoration': 'none'},
                    href='/hpath/view/multi'
                ),
            ],
            style={'width': '400px'}
        )
    ]
)
