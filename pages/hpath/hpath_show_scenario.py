"""Page for showing results for a single simulation scenario."""
import logging

import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import requests

from dash import Input, Output, State, callback, dcc, html
from dash_compose import composition
from plotly import express as px

import kpis
from conf import HPATH_RESTFUL_HOST, LAB_TAT_TARGET, TAT_TARGET
from pages import templates

dash.register_page(
    __name__,
    title='Histopathology: Scenario Results',
    path_template='/hpath/view/single/<scenario_id>'
)

auto_col_style = {'width': 'auto', 'class_name': 'p-2'}
tat_col_style = {
    'class_name': 'p-2',
    'md': 12,
    'lg': 6,
    'xl': 6,
    'xxl': 4,
}

table_plot_left_style = {  # Table in a table-plot combination
    'class_name': 'p-2',
    'width': 'auto'
}

table_plot_tat_right_style = {  # Table in a table-plot combination
    'class_name': 'p-2',
    'md': 12,
    'lg': 7
}

table_plot_util_right_style = {  # Table in a table-plot combination
    'class_name': 'p-2',
    'lg': 12,
    'xl': 7,
    'xxl': 8,
}

slider_style = {
    'style': {'width': '100%'},
    'className': 'p-0 my-2'
}

plots_container_style = {'fluid': True, 'class_name': 'p-0'}

UTIL_LATEX = [
    r"$\text{mean utilisation}=\frac"
    r"{\int_{0}^{T}\text{number busy}\left(t\right)\mathrm{d}t}"
    r"{\int_{0}^{T}\text{number allocated}\left(t\right)\mathrm{d}t}$"
    ", where $T$ is the duration of the simulation."
]

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
        report = kpis.Report.model_validate_json(results['results'])
        report_jsonstr = kpis.Report.model_dump_json(report)
    except Exception as exc:
        logger.error(str(exc))
        report = None

    with html.Div(id='scenario-result', className='mt-3 mx-3') as div:
        yield templates.breadcrumb(
            ['Home', 'Histopathology: Simulator', 'Scenarios', f'{scenario_id}'],
            ['hpath', 'view', 'single']
        )
        yield templates.page_title('Histopathology: Single-Scenario Results')

        yield dcc.Store(id='scenario-report', data=report_jsonstr)
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

        with dbc.Accordion(class_name='sim-results-accordion mb-5'):

            ####################################
            ##                                ##
            ##  ########    ###    ########   ##
            ##     ##      ## ##      ##      ##
            ##     ##     ##   ##     ##      ##
            ##     ##    ##     ##    ##      ##
            ##     ##    #########    ##      ##
            ##     ##    ##     ##    ##      ##
            ##     ##    ##     ##    ##      ##
            ##                                ##
            ####################################

            with dbc.AccordionItem(title="Turnaround Times"):
                with dbc.Container(fluid=True):
                    with dbc.Row(class_name='d-flex mx-0'):
                        # CARD: Summary
                        with dbc.Col(**tat_col_style, id='card-tat-summary'):
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

                        # CARD: TAT Targets
                        with dbc.Col(**tat_col_style, id='card-tat-targets'):
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

                        # CARD: Lab TAT Target
                        with dbc.Col(**tat_col_style, id='card-lab-tat-target'):
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

            ########################################################################
            ##                                                                    ##
            ##  ########    ###    ########                                       ##
            ##     ##      ## ##      ##                                          ##
            ##     ##     ##   ##     ##                                          ##
            ##     ##    ##     ##    ##                                          ##
            ##     ##    #########    ##                                          ##
            ##     ##    ##     ##    ##                                          ##
            ##     ##    ##     ##    ##                                          ##
            ##                                                                    ##
            ##    ###     ######  ########    ###     ######   ########    ###    ##
            ##   ##      ##    ##    ##      ## ##   ##    ##  ##            ##   ##
            ##  ##       ##          ##     ##   ##  ##        ##             ##  ##
            ##  ##        ######     ##    ##     ## ##   #### ######         ##  ##
            ##  ##             ##    ##    ######### ##    ##  ##             ##  ##
            ##   ##      ##    ##    ##    ##     ## ##    ##  ##            ##   ##
            ##    ###     ######     ##    ##     ##  ######   ########    ###    ##
            ##                                                                    ##
            ########################################################################

            df_tat_by_stage = pd.DataFrame({
                '#': [str(n) for n in range(1, len(report.tat_by_stage.x) + 1)],
                'Stage': report.tat_by_stage.x,
                'TAT': report.tat_by_stage.y
            })
            df_tat_by_stage_sorted = df_tat_by_stage\
                .sort_values(by=['TAT'], ascending=False)\
                .rename(columns={"TAT": "TAT ↓"})
            df_tat_by_stage_sorted['TAT ↓']\
                = [f'{y:.2f} hours' if y >= 1 else f'{(y*60):.1f} min'  # pylint:disable=E1136,E1137
                   for y in df_tat_by_stage_sorted['TAT ↓']]  # pylint:disable=E1136,E1137

            # Layout
            with dbc.AccordionItem(title="TAT by Stage"):
                with dbc.Container(fluid=True):
                    with dbc.Row(class_name='d-flex mx-0'):
                        with dbc.Col(**table_plot_left_style):
                            yield dbc.Table.from_dataframe(
                                df_tat_by_stage_sorted,
                                striped=True, bordered=True, hover=True,
                                class_name='mb-0 right-align-last'
                            )
                        with dbc.Col(**table_plot_tat_right_style):
                            yield dcc.Graph(
                                figure=px.bar(
                                    df_tat_by_stage,
                                    x='Stage',
                                    y='TAT',
                                    title='Turnaround Time by Stage',
                                    labels={
                                        'TAT': 'Turnaround time (hours)'
                                    },
                                    height=400
                                )
                            )
                            with html.Div():
                                yield html.B('Note: ')
                                yield 'Stage TATs do not include delivery delays to the next stage.'

            ###################################################################################
            ##                                                                               ##
            ##  ########  ########  ######   #######  ##     ## ########   ######  ########  ##
            ##  ##     ## ##       ##    ## ##     ## ##     ## ##     ## ##    ## ##        ##
            ##  ##     ## ##       ##       ##     ## ##     ## ##     ## ##       ##        ##
            ##  ########  ######    ######  ##     ## ##     ## ########  ##       ######    ##
            ##  ##   ##   ##             ## ##     ## ##     ## ##   ##   ##       ##        ##
            ##  ##    ##  ##       ##    ## ##     ## ##     ## ##    ##  ##    ## ##        ##
            ##  ##     ## ########  ######   #######   #######  ##     ##  ######  ########  ##
            ##                                                                               ##
            ##     ###    ##       ##        #######   ######                                ##
            ##    ## ##   ##       ##       ##     ## ##    ##                               ##
            ##   ##   ##  ##       ##       ##     ## ##                                     ##
            ##  ##     ## ##       ##       ##     ## ##                                     ##
            ##  ######### ##       ##       ##     ## ##                                     ##
            ##  ##     ## ##       ##       ##     ## ##    ##                               ##
            ##  ##     ## ######## ########  #######   ######                                ##
            ##                                                                               ##
            ###################################################################################

            with dbc.AccordionItem(title="Resource Allocation"):
                with dbc.Stack(gap=3):
                    with html.P(className='mb-0'):
                        yield (
                            'Select which resources to show from the dropdown '
                            'checkbox menu below. ('
                        )
                        yield html.B('Default: ')
                        yield 'all resources)'

                    with dbc.Row():
                        with dbc.Col(class_name='p-2'):
                            # NOTE: Multi-value dcc.Dropdown does not support dragging to reorder
                            # selected options.  Find another solution?
                            yield dcc.Dropdown(
                                id='multi-dropdown-res-alloc',
                                options=list(report.resource_allocation.keys()),
                                value=list(report.resource_allocation.keys()),
                                multi=True
                            )
                        with dbc.Col(width='auto', class_name='p-2'):
                            yield dbc.Button('Add all', id='view-res-alloc-all')

                    with dbc.Row():
                        with dbc.Col(width='auto', class_name='p-2'):
                            with dbc.ButtonGroup():
                                yield dcc.Store(
                                    id='view-res-alloc-layout-value',
                                    data='medium'
                                )
                                with dbc.Button(
                                    id='view-res-alloc-btn-wide',
                                    color='dark'
                                ):
                                    yield html.Span(className='fa-solid fa-square')
                                    yield '\u2002Wide View'
                                with dbc.Button(
                                    id='view-res-alloc-btn-medium',
                                    color='dark'
                                ):
                                    yield html.Span(className='fa-solid fa-pause')
                                    yield '\u2002Medium View'
                                with dbc.Button(
                                    id='view-res-alloc-btn-narrow',
                                    color='dark'
                                ):
                                    yield html.Span(className='fa-solid fa-bars fa-rotate-90')
                                    yield '\u2002Narrow View'
                        with dbc.Col(width='auto', class_name='p-2'):
                            with dbc.InputGroup():
                                yield dbc.InputGroupText('Time unit:')
                                yield dbc.Select(
                                    id='select-res-alloc-timeunit',
                                    options=['weeks', 'days', 'hours'],
                                    value='days'
                                )

                    with dbc.Row():
                        with dbc.Col(width=12, class_name='p-2'):
                            yield dbc.Container(id='container-res-alloc', **plots_container_style)

            ########################################################################
            ##                                                                    ##
            ##  ##      ## #### ########                                          ##
            ##  ##  ##  ##  ##  ##     ##                                         ##
            ##  ##  ##  ##  ##  ##     ##                                         ##
            ##  ##  ##  ##  ##  ########                                          ##
            ##  ##  ##  ##  ##  ##                                                ##
            ##  ##  ##  ##  ##  ##                                                ##
            ##   ###  ###  #### ##                                                ##
            ##                                                                    ##
            ##    ###     ######  ########    ###     ######   ########    ###    ##
            ##   ##      ##    ##    ##      ## ##   ##    ##  ##            ##   ##
            ##  ##       ##          ##     ##   ##  ##        ##             ##  ##
            ##  ##        ######     ##    ##     ## ##   #### ######         ##  ##
            ##  ##             ##    ##    ######### ##    ##  ##             ##  ##
            ##   ##      ##    ##    ##    ##     ## ##    ##  ##            ##   ##
            ##    ###     ######     ##    ##     ##  ######   ########    ###    ##
            ##                                                                    ##
            ########################################################################
            with dbc.AccordionItem(title="Work-in-Progress by Stage"):
                with dbc.Stack(gap=3):
                    with html.P(className='mb-0'):
                        yield 'Select which resources to show from the menu below. ('
                        yield html.B('Default: ')
                        yield 'all stages)'

                    # NOTE: Multi-value dcc.Dropdown does not support dragging to reorder
                    # selected options.  Find another solution?
                    with dbc.Row():
                        with dbc.Col(class_name='p-2'):
                            yield dcc.Dropdown(
                                id='multi-dropdown-wip',
                                options=list(report.wip_by_stage.labels),
                                value=list(report.wip_by_stage.labels),
                                multi=True
                            )
                        with dbc.Col(width='auto', class_name='p-2'):
                            yield dbc.Button('Add all', id='view-wip-all')

                    with dbc.Row():
                        with dbc.Col(width='auto', class_name='p-2'):
                            with dbc.ButtonGroup():
                                yield dcc.Store(
                                    id='view-wip-layout-value',
                                    data='medium'
                                )
                                with dbc.Button(
                                    id='view-wip-btn-wide',
                                    color='dark'
                                ):
                                    yield html.Span(className='fa-solid fa-square')
                                    yield '\u2002Wide View'
                                with dbc.Button(
                                    id='view-wip-btn-medium',
                                    color='dark'
                                ):
                                    yield html.Span(className='fa-solid fa-pause')
                                    yield '\u2002Medium View'
                                with dbc.Button(
                                    id='view-wip-btn-narrow',
                                    color='dark'
                                ):
                                    yield html.Span(className='fa-solid fa-bars fa-rotate-90')
                                    yield '\u2002Narrow View'
                        with dbc.Col(width='auto', class_name='p-2'):
                            with dbc.InputGroup():
                                yield dbc.InputGroupText('Time unit:')
                                yield dbc.Select(
                                    id='select-wip-timeunit',
                                    options=['weeks', 'days', 'hours'],
                                    value='days'
                                )

                    with dbc.Row():
                        with dbc.Col(width=12, class_name='p-2'):
                            yield dbc.Container(id='container-wip', **plots_container_style)

            ########################################
            ##                                    ##
            ##  ##     ## ######## #### ##        ##
            ##  ##     ##    ##     ##  ##        ##
            ##  ##     ##    ##     ##  ##        ##
            ##  ##     ##    ##     ##  ##        ##
            ##  ##     ##    ##     ##  ##        ##
            ##  ##     ##    ##     ##  ##        ##
            ##   #######     ##    #### ########  ##
            ##                                    ##
            ########################################

            # Computation
            df_util = pd.DataFrame({
                'Resource': report.utilization_by_resource.x,
                'Utilisation': report.utilization_by_resource.y
            })
            df_util_sorted = df_util\
                .sort_values(by=['Utilisation'], ascending=False)\
                .rename(columns={"Utilisation": "Utilisation ↓"})
            df_util_sorted["Utilisation ↓"]\
                = [f'{y:.2%}' for y in df_util_sorted["Utilisation ↓"]]

            # Layout
            with dbc.AccordionItem(title="Utilisation by Resource"):
                with dbc.Container(fluid=True):
                    yield dcc.Markdown(UTIL_LATEX, mathjax=True, style={'font-size': '1.2rem'})
                    with html.Div(className='mb-4'):
                        yield(
                            'This can be understood as the ratio of the areas under the '
                            '"Number busy" and "Number allocated" curves and handles situations '
                            'where deallocated resources are still finishing their current task.'
                        )
                    with dbc.Row(class_name='d-flex mx-0'):
                        with dbc.Col(**table_plot_left_style):
                            yield dbc.Table.from_dataframe(
                                df_util_sorted,
                                striped=True, bordered=True, hover=True,
                                class_name='mb-0 right-align-last'
                            )
                        with dbc.Col(**table_plot_util_right_style):
                            bar_chart = px.bar(
                                df_util,
                                x='Resource',
                                y='Utilisation',
                                title='Utilisation by Resource',
                                labels={
                                    'Utilisation': 'Utilisation'
                                },
                                height=600
                            )
                            bar_chart.update_layout(
                                yaxis_tickformat='.0%'
                            )
                            yield dcc.Graph(figure=bar_chart)
                            with html.Div():
                                yield html.B('Note: ')
                                yield 'Stage TATs do not include delivery delays to the next stage.'

            #############################################################################
            ##                                                                         ##
            ##  ##     ## ######## #### ##                                             ##
            ##  ##     ##    ##     ##  ##                                             ##
            ##  ##     ##    ##     ##  ##                                             ##
            ##  ##     ##    ##     ##  ##                                             ##
            ##  ##     ##    ##     ##  ##                                             ##
            ##  ##     ##    ##     ##  ##                                             ##
            ##   #######     ##    #### ########                                       ##
            ##                                                                         ##
            ##                                                                         ##
            ##    ### ##     ##  #######  ##     ## ########  ##       ##    ## ###    ##
            ##   ##   ##     ## ##     ## ##     ## ##     ## ##        ##  ##    ##   ##
            ##  ##    ##     ## ##     ## ##     ## ##     ## ##         ####      ##  ##
            ##  ##    ######### ##     ## ##     ## ########  ##          ##       ##  ##
            ##  ##    ##     ## ##     ## ##     ## ##   ##   ##          ##       ##  ##
            ##   ##   ##     ## ##     ## ##     ## ##    ##  ##          ##      ##   ##
            ##    ### ##     ##  #######   #######  ##     ## ########    ##    ###    ##
            ##                                                                         ##
            #############################################################################

            with dbc.AccordionItem(title="Utilisation by Resource (hourly)"):
                with dbc.Stack(gap=3):
                    with html.P(className='mb-0'):
                        yield 'Select which resources to show from the menu below. ('
                        yield html.B('Default: ')
                        yield 'all resources)'

                    with dbc.Row():
                        with dbc.Col(class_name='p-2'):
                            # NOTE: Multi-value dcc.Dropdown does not support dragging to reorder
                            # selected options.  Find another solution?
                            yield dcc.Dropdown(
                                id='multi-dropdown-util-hourly',
                                options=list(report.resource_allocation.keys()),
                                value=list(report.resource_allocation.keys()),
                                multi=True
                            )
                        with dbc.Col(width='auto', class_name='p-2'):
                            yield dbc.Button('Add all', id='view-util-hourly-all')

                    with dbc.Row():
                        with dbc.Col(width='auto', class_name='p-2'):
                            with dbc.ButtonGroup():
                                yield dcc.Store(
                                    id='view-util-hourly-layout-value',
                                    data='medium'
                                )
                                with dbc.Button(
                                    id='view-util-hourly-btn-wide',
                                    color='dark'
                                ):
                                    yield html.Span(className='fa-solid fa-square')
                                    yield '\u2002Wide View'
                                with dbc.Button(
                                    id='view-util-hourly-btn-medium',
                                    color='dark'
                                ):
                                    yield html.Span(className='fa-solid fa-pause')
                                    yield '\u2002Medium View'
                                with dbc.Button(
                                    id='view-util-hourly-btn-narrow',
                                    color='dark'
                                ):
                                    yield html.Span(className='fa-solid fa-bars fa-rotate-90')
                                    yield '\u2002Narrow View'
                        with dbc.Col(width='auto', class_name='p-2'):
                            with dbc.InputGroup():
                                yield dbc.InputGroupText('Time unit:')
                                yield dbc.Select(
                                    id='select-util-hourly-timeunit',
                                    options=['weeks', 'days', 'hours'],
                                    value='days'
                                )

                    with dbc.Row():
                        with dbc.Col(width=12, class_name='p-2'):
                            yield dbc.Container(id='container-util-hourly', **plots_container_style)

    return div

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

# CHANGE PLOT WIDTHS

@callback(
    Output('view-res-alloc-layout-value', 'data'),
    Input('view-res-alloc-btn-wide', 'n_clicks'),
    Input('view-res-alloc-btn-medium', 'n_clicks'),
    Input('view-res-alloc-btn-narrow', 'n_clicks'),
    prevent_initial_call=True
)
def change_res_alloc_width(*_):
    """Change width of plots in the Resource Allocation panel."""
    if dash.ctx.triggered_id == 'view-res-alloc-btn-wide':
        return 'wide'
    if dash.ctx.triggered_id == 'view-res-alloc-btn-medium':
        return 'medium'
    if dash.ctx.triggered_id == 'view-res-alloc-btn-narrow':
        return 'narrow'
    return dash.no_update


@callback(
    Output('view-wip-layout-value', 'data'),
    Input('view-wip-btn-wide', 'n_clicks'),
    Input('view-wip-btn-medium', 'n_clicks'),
    Input('view-wip-btn-narrow', 'n_clicks'),
    prevent_initial_call=True
)
def change_wip_width(*_):
    """Change width of plots in the WIP by Stage panel."""
    if dash.ctx.triggered_id == 'view-wip-btn-wide':
        return 'wide'
    if dash.ctx.triggered_id == 'view-wip-btn-medium':
        return 'medium'
    if dash.ctx.triggered_id == 'view-wip-btn-narrow':
        return 'narrow'
    return dash.no_update


@callback(
    Output('view-util-hourly-layout-value', 'data'),
    Input('view-util-hourly-btn-wide', 'n_clicks'),
    Input('view-util-hourly-btn-medium', 'n_clicks'),
    Input('view-util-hourly-btn-narrow', 'n_clicks'),
    prevent_initial_call=True
)
def change_util_hourly_width(*_):
    """Change width of plots in the Resource Allocation panel."""
    if dash.ctx.triggered_id == 'view-util-hourly-btn-wide':
        return 'wide'
    if dash.ctx.triggered_id == 'view-util-hourly-btn-medium':
        return 'medium'
    if dash.ctx.triggered_id == 'view-util-hourly-btn-narrow':
        return 'narrow'
    return dash.no_update


@callback(
    Output('multi-dropdown-res-alloc', 'value'),
    Input('view-res-alloc-all', 'n_clicks'),
    State('multi-dropdown-res-alloc', 'options'),
    prevent_initial_call=True
)
def select_all_res_alloc(_, options):
    """Callback when "Add all" button is clicked for Resource Allocation view."""
    return options


@callback(
    Output('multi-dropdown-wip', 'value'),
    Input('view-wip-all', 'n_clicks'),
    State('multi-dropdown-wip', 'options'),
    prevent_initial_call=True
)
def select_all_wip(_, options):
    """Callback when "Add all" button is clicked for WIP by Stage view."""
    return options


@callback(
    Output('multi-dropdown-util-hourly', 'value'),
    Input('view-util-hourly-all', 'n_clicks'),
    State('multi-dropdown-util-hourly', 'options'),
    prevent_initial_call=True
)
def select_all_util_hourly(_, options):
    """Callback when "Add all" button is clicked for Hourly Utilisation view."""
    return options

# PLOTS

# BUG: Plotly fails to render if too many plots/data points???

PLOTS_TODO_MSG = """\
**TODO**:

One line chart per selected option in the multi-`Select` component above, with time units as
specified in the `Select` component and figure width as specified in the Store component.

Wrap the plots in a `dbc.Container`, with 1, 2, or 3 `dbc.Col` per `dbc.Row`
depending on whether the specified column width is 12 (wide), 6 (medium), or 4 (narrow).
"""


@callback(
    Output('container-res-alloc', 'children'),
    Input('multi-dropdown-res-alloc', 'value'),  # Multi-select: which plots to display
    Input('view-res-alloc-layout-value', 'data'),  # Store: display width
    Input('select-res-alloc-timeunit', 'value'),  # Store: x-axis time unit
    State('scenario-report', 'data')  # Simulation results
)
@composition
def gen_res_alloc_plots(selected, width, time_unit, data):
    """Generate plots for resource allocations over time."""
    cols = 12 if width == 'wide' else 6 if width == 'medium' else 4
    scale = 168 if time_unit == 'weeks' else 24 if time_unit == 'days' else 1
    charts_data = kpis.Report.model_validate_json(data).resource_allocation
    with dbc.Container(fluid=True) as ret:
        with dbc.Row():  # Place all plots in a single Row as bootstrap will handle line wrapping
            for res in selected:
                df = pd.DataFrame({
                    f'Time ({time_unit})': np.array(charts_data[res].x)/scale,
                    '# Allocated': charts_data[res].y
                })
                plot = px.line(
                    df,
                    x=f'Time ({time_unit})',
                    y='# Allocated',
                    title=res,
                    render_mode='svg'
                ).update_traces(
                    line_shape="hv"
                )
                if time_unit == 'days':
                    plot.update_xaxes(dtick=7, tick0=0)  # weekly ticks
                with dbc.Col(width=cols):
                    yield dcc.Graph(figure=plot)
    return ret


@callback(
    Output('container-wip', 'children'),
    Input('multi-dropdown-wip', 'value'),  # Multi-select: which plots to display
    Input('view-wip-layout-value', 'data'),  # Store: display width
    Input('select-wip-timeunit', 'value'),  # Store: x-axis time unit
    State('scenario-report', 'data')  # Simulation results
)
@composition
def gen_wip_plots(selected, width, time_unit, data):
    """Generate plots for resource allocations over time."""
    cols = 12 if width == 'wide' else 6 if width == 'medium' else 4
    scale = 168 if time_unit == 'weeks' else 24 if time_unit == 'days' else 1
    charts_data = kpis.Report.model_validate_json(data).wip_by_stage
    df = pd.DataFrame(
        data=np.array(charts_data.y).T,
        index=np.array(charts_data.x)/scale,
        columns=charts_data.labels
    ).reset_index()
    with dbc.Container(fluid=True) as ret:
        with dbc.Row():  # Place all plots in a single Row as bootstrap will handle line wrapping
            for stage in selected:
                plot = px.line(
                    df,
                    x="index",
                    y=stage,
                    title=stage,
                    render_mode='svg'
                ).update_traces(
                    line_shape="hv"
                ).update_xaxes(
                    title=f'Time ({time_unit})'
                ).update_yaxes(
                    title='Hourly mean WIP'
                )
                if time_unit == 'days':
                    plot.update_xaxes(dtick=7, tick0=0)  # weekly ticks
                with dbc.Col(width=cols):
                    yield dcc.Graph(figure=plot)
    return ret


@callback(
    Output('container-util-hourly', 'children'),
    Input('multi-dropdown-util-hourly', 'value'),  # Multi-select: which plots to display
    Input('view-util-hourly-layout-value', 'data'),  # Store: display width
    Input('select-util-hourly-timeunit', 'value'),  # Store: x-axis time unit
    State('scenario-report', 'data')  # Simulation results
)
@composition
def gen_util_hourly_plots(selected, width, time_unit, data):
    """Generate plots for resource allocations over time."""
    cols = 12 if width == 'wide' else 6 if width == 'medium' else 4
    scale = 168 if time_unit == 'weeks' else 24 if time_unit == 'days' else 1
    charts_data = kpis.Report.model_validate_json(data).hourly_utilization_by_resource
    df = pd.DataFrame(
        data=np.array(charts_data.y).T,
        index=np.array(charts_data.x)/scale,
        columns=charts_data.labels
    ).reset_index()
    with dbc.Container(fluid=True) as ret:
        with dbc.Row():  # Place all plots in a single Row as bootstrap will handle line wrapping
            for resource in selected:
                plot = px.line(
                    df,
                    x="index",
                    y=resource,
                    title=resource,
                    render_mode='svg'
                ).update_traces(
                    line_shape="hv"
                ).update_xaxes(
                    title=f'Time ({time_unit})'
                ).update_yaxes(
                    title='Mean # busy (hourly)'
                )
                if time_unit == 'days':
                    plot.update_xaxes(dtick=7, tick0=0)  # weekly ticks
                with dbc.Col(width=cols):
                    yield dcc.Graph(figure=plot)
    return ret
