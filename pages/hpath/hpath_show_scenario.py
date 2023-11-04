"""Page for showing results for a single simulation scenario."""
import json
import logging

import dash
import dash_bootstrap_components as dbc
from dash import callback, Input, Output
from dash_compose import composition
import requests

import kpis
from conf import HPATH_RESTFUL_HOST
from dash import dcc, html
from pages import templates

dash.register_page(
    __name__,
    title='Histopathology: Scenario Results',
    path_template='/hpath/view/single/<scenario_id>'
)

@composition
def layout(scenario_id: int):
    """Build the page layout to show the given scenario's result."""
    logger = logging.getLogger('dash.dash')

    try:
        results = requests.get(
            f'{HPATH_RESTFUL_HOST}/scenarios/{scenario_id}/results/',
            timeout=10
        ).json()[0]
        report = kpis.Report(**json.loads(results['results']))
    except Exception as exc:
        logger.error(str(exc))
        report = None

    with html.Div(id='scenario-result', className='mt-3 mx-3') as div:
        yield templates.breadcrumb(
            ['Home', 'Histopathology: Simulator', 'Scenarios', f'{scenario_id}'],
            ['hpath', 'view', 'single']
        )
        yield templates.page_title('Histopathology: Single-Scenario Results')
        if report is None:
            with html.Div(style={'color': '#a00'}):
                yield html.B('Error: ')
                yield html.Span(f"Could not fetch scenario with ID: {scenario_id}")
        else:
            yield html.H2(
                f"Scenario #{scenario_id}: {results['scenario_name']}",
                style={'font-size': '1.4rem'}
            )

    return div
