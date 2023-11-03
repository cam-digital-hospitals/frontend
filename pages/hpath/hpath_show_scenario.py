"""Page for showing results for a single simulation scenario."""
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

from pages import templates

dash.register_page(
    __name__,
    title='Histopathology: Scenario Results',
    path_template='/hpath/view/single/<scenario_id>'
)


def layout(scenario_id=None):
    """Build the layout to show the given scenario's result.
    """
    # TODO fetch result, if error show error message
    result = None

    # TODO replicate Lakee's result page?
    return dbc.Stack(
        [
            templates.breadcrumb(
                ['Home', 'Histopathology: Simulator', 'Scenarios', f'{scenario_id}'],
                ['hpath', 'view', 'single']
            ),
            templates.page_title('Histopathology: Single-Scenario Results'),

            (  # ternary statement
                html.Div(
                    [
                        html.B('Error: '),
                        html.Span(f"Could not fetch scenario with ID: {scenario_id}")
                    ],
                    style={'color': '#a00'}
                ) if result is None else
                html.H2(
                    result.sc_name,
                    style={'font-size': '2.2rem'}
                )
            )  # end ternary statement
        ]
    )
