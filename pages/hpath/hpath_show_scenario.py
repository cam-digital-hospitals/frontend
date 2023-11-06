"""Page for showing results for a single simulation scenario."""
import json
import logging

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash_compose import composition
import pandas as pd
from plotly import express as px
import requests

import kpis
from conf import HPATH_RESTFUL_HOST, TAT_TARGET, LAB_TAT_TARGET
from pages import templates


dash.register_page(
    __name__,
    title='Histopathology: Scenario Results',
    path_template='/hpath/view/single/<scenario_id>'
)

auto_col_style = {'width': 'auto', 'class_name': 'p-0'}
slider_style = {
    'style': {'width': '500px', 'margin-top': '-20px !important'},
    'className': 'p-0 my-2'
}


@composition
def layout(scenario_id: int):
    """Build the page layout to show the given scenario's result."""
    logger = logging.getLogger('dash.dash')

    def d_h(hours):
        return f'{int(hours // 24)} days {(hours % 24):.2f} hours'

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
                return div  # NOTE: OMIT REST OF LAYOUT BELOW
        else:
            yield html.H2(
                f"Scenario #{scenario_id}: {results['scenario_name']}",
                style={'font-size': '1.4rem'}
            )

        with dbc.Stack(gap=3, class_name='mb-5'):
            # CARD: Turnaround Times
            with dbc.Card(style={'border': 'dashed 1px darkred'}):
                with dbc.CardBody():
                    yield html.H1(
                        "Turnaround Times",
                        style={'font-size': '2.2rem'}
                    )

                    with dbc.Row(class_name='d-flex gap-3 mx-0'):
                        # SUB-CARD: Summary
                        with dbc.Col(**auto_col_style):
                            with dbc.Card(style={'height': '100%'}):
                                with dbc.CardBody():
                                    with html.Div(style={'font-size': '1.4rem'}):
                                        yield html.B("Overall TAT: ")
                                        yield d_h(report.overall_tat)
                                    with html.Div(style={'font-size': '1rem'}):
                                        yield f'({report.overall_tat:.2f} hours)'
                                    with html.Div(style={'font-size': '1.4rem'}):
                                        yield html.B("Lab TAT: ")
                                        yield d_h(report.lab_tat)
                                    with html.Div(style={'font-size': '1rem'}):
                                        yield f'({report.lab_tat:.2f} hours)'

                        # SUB-CARD: TAT Targets
                        with dbc.Col(**auto_col_style):
                            with dbc.Card(style={'height': '100%'}):
                                with dbc.CardBody():
                                    yield html.B(
                                        "TAT Targets",
                                        style={'font-size': '1.4rem'}
                                    )
                                    with dbc.Stack(class_name='gap-1 mx-0'):
                                        for n in ['7', '10', '12', '21']:
                                            with html.Div():
                                                yield f'≤ {n} days:'
                                            with html.Div(**slider_style):

                                                good = report.progress[n] > TAT_TARGET[n]

                                                marks = {}
                                                target = round(TAT_TARGET[n]*100)
                                                marks[str(target)] \
                                                    = {'label': f'Target: {TAT_TARGET[n]:.0%}'}

                                                if target >= 10:
                                                    marks['0'] = {'label': '0%'}
                                                if target <= 90:
                                                    marks['100'] = {'label': '100%'}

                                                yield dcc.Slider(
                                                    0, 100, step=0.01,
                                                    marks=marks,
                                                    value=round(report.progress[n]*100, 2),
                                                    disabled=True,
                                                    tooltip={
                                                        "placement": "top",
                                                        "always_visible": True
                                                    },
                                                    className="tat-slider tat-slider-"
                                                        f"{'good' if good else 'bad'}"
                                                )

                        # SUB-CARD: Lab TAT Target
                        with dbc.Col(**auto_col_style):
                            with dbc.Card(style={'height': '100%'}):
                                with dbc.CardBody():
                                    yield html.B(
                                        "Lab TAT Target",
                                        style={'font-size': '1.4rem'}
                                    )
                                    with dbc.Stack(class_name='gap-1 mx-0'):
                                        with html.Div():
                                            yield '≤ 3 days:'
                                        with html.Div(**slider_style):

                                            good = report.lab_progress['3'] > LAB_TAT_TARGET['3']

                                            marks = {}
                                            target = round(LAB_TAT_TARGET['3']*100)
                                            marks[str(target)] = {
                                                'label': f'Target: {LAB_TAT_TARGET["3"]:.0%}'
                                            }

                                            if target >= 10:
                                                marks['0'] = {'label': '0%'}
                                            if target <= 90:
                                                marks['100'] = {'label': '100%'}

                                            yield dcc.Slider(
                                                0, 100, step=0.01,
                                                marks=marks,
                                                value=round(report.lab_progress['3']*100, 2),
                                                disabled=True,
                                                tooltip={
                                                    "placement": "top", "always_visible": True
                                                },
                                                className="tat-slider tat-slider-"
                                                        f"{'good' if good else 'bad'}"
                                            )

            # CARD: TAT by stage
            df_tat_by_stage = pd.DataFrame({
                '#': range(1, len(report.tat_by_stage['x']) + 1),
                'Stage': report.tat_by_stage['x'],
                'TAT': report.tat_by_stage['y']
            })
            df_tat_by_stage_sorted = df_tat_by_stage.sort_values(by=['TAT'], ascending=False)
            df_tat_by_stage_sorted['TAT']\
                = [f'{x:.2f} hours' if x >= 1 else f'{(x*60):.1f} min'  # pylint:disable=E1136,E1137
                   for x in df_tat_by_stage_sorted['TAT']]  # pylint:disable=E1136,E1137
            df_tat_by_stage_sorted.rename(columns={"TAT": "TAT ↓"})

            with dbc.Card(style={'border': 'dashed 1px darkred'}):
                with dbc.CardBody():
                    with dbc.Row(class_name='d-flex flex-row gap-3 mx-0'):
                        # SUB-CARD: table
                        with dbc.Col(**auto_col_style):
                            yield html.H1(
                                "TAT by Stage",
                                style={'font-size': '2.2rem'}
                            )

                            yield dbc.Table.from_dataframe(
                                df_tat_by_stage_sorted,
                                striped=True, bordered=True, hover=True,
                                class_name='mb-0'
                            )
                        with dbc.Col(width=True, class_name='p-0'):
                            # FIXME: stop graph from falling to the next line when window is resized
                            yield dcc.Graph(
                                figure=px.bar(
                                    df_tat_by_stage,
                                    x='Stage',
                                    y='TAT',
                                    title='Turnaround Time by Stage',
                                    labels={
                                        'TAT': 'Turnaround time (hours)'
                                    },
                                    #width=600,
                                    height=400
                                )
                            )
                            with html.Div():
                                yield html.B('Note: ')
                                yield 'Stage TATs do not include delivery delays to the next stage.'

    return div
