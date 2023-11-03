"""Menu page for the Histopathology Simulator."""
import dash
import dash_bootstrap_components as dbc

from pages import templates

dash.register_page(__name__, title='Histopathology', path='/hpath')


def btn_hpath_submit():
    """Contents of the "Submit Simulation Job" button, i.e. dbc.Button.children."""
    return [
        templates.card_header(
            'Submit Simulation Job',
            'square-caret-right',
            regular=True,
            pad_below=False
        ),
    ]


def btn_hpath_results():
    """Contents of the "View Results" button, i.e. dbc.Button.children."""
    return [
        templates.card_header('View Results', 'search', pad_below=False)
    ]


btn_style = {'color': 'info', 'style': {'height': '100%'}}
auto_col_style = {'width': 'auto', 'class_name': 'p-0'}

btn_submit_page = dbc.Button(
    btn_hpath_submit(),
    href='/hpath/submit',
    **btn_style
)

btn_view_page = dbc.Button(
    btn_hpath_results(),
    href='/hpath/view',
    **btn_style
)


layout = dbc.Stack(
    [
        templates.breadcrumb(
            ['Home', 'Histopathology: Simulator'], ['hpath']
        ),
        templates.page_title('Histopathology: Simulator'),
        dbc.Row(
            [
                dbc.Col(
                    btn_submit_page,
                    **auto_col_style
                ),
                dbc.Col(
                    btn_view_page,
                    **auto_col_style
                )
            ],
            class_name='d-flex gap-3 mx-0 mt-3'
        )
    ]
)
