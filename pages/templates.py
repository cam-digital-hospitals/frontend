"""Template Dash components for the dashboards app."""
from dash import html
import dash_bootstrap_components as dbc

# All page contents are to be rendered as `dbc.Stack`s
# and should use dbc.Row and dbc.Col for layout


def card_header(title, icon=None, *, pad_below=True, regular=False, color=None) -> html.Div:
    """Card or Button header with optional icon.

    If there is no body below the header, set pad_below to False.
    """
    children = [html.Span(title, className='px-1')]
    if icon is not None:
        children.insert(
            0,
            html.Span(
                className=(
                    f'fa-regular fa-{icon} px-1' if regular
                    else f'fa fa-{icon} px-1'
                ),
                style={'color': color} if color is not None else None
            ),
        )
    return html.Div(
        children=children,
        className='card-title' if pad_below else '',
        style={'font-size': '1.6rem'}
    )


def labelled_input(label, id, *, align='start', disabled=False, prompt=None) -> dbc.Col:
    """Text input with label as a dbc.Col, for use in a dbc.Row."""
    return dbc.Col(
        dbc.Row(
            [
                dbc.Col(
                    dbc.Label([html.B(label), ': '], class_name='m-0'),
                    width="auto",
                    class_name='pe-0'
                ),
                dbc.Col(
                    dbc.Input(
                        id=id,
                        disabled=disabled,
                        placeholder=prompt
                    ),
                    width="auto"
                )
            ],
            align=align
        ),
        width='auto',
        class_name='m-0'
    )


def labelled_numeric(
        label, id, *,
        disabled=False, init=0,
        unit_selector=None,
) -> dbc.Col:
    """Numeric input with label as a dbc.Col, for use in a dbc.Row."""
    row_components = [
        dbc.Col(
            dbc.Label([html.B(label), ': '], class_name='m-0'),
            width="auto",
            class_name='pe-0'
        ),
        dbc.Col(
            dbc.Input(
                id=id,
                disabled=disabled,
                type="number",
                min=0,
                value=init,
                style={'width': '100px', 'max-width': '100px'},
            ),
            width='auto',
            class_name='pe-0',
        ),
    ]
    if unit_selector is not None:
        row_components.append(dbc.Col(unit_selector, class_name='ps-0'))

    return dbc.Col(
        dbc.Row(
            row_components,
            align="start",
            justify="start"
        ),
        width='auto',
        class_name='m-0'
    )


def breadcrumb(labels, path_fragments) -> dbc.Breadcrumb:
    """Creates a breadcrumb, e.g. "Home / Histopathology: Simulator / Submit simulation job".
    Each level of the breadcrumb except the last is a link.
    """
    # Paths should be one element shorter than labels
    # Example: breadcrumb(["Home", "Hpath Simulator", "Run Sim"], ["hpath", "submit"])
    paths = ['/'+'/'.join(path_fragments[:n]) for n in range(len(path_fragments)+1)]
    items = [
        {'label': label, 'href': path}
        for label, path in zip(labels, paths)
    ]
    del items[-1]['href']
    items[-1]['active'] = True
    return dbc.Breadcrumb(items=items, class_name='mx-0')


def page_title(title_str) -> dbc.Row:
    """Renders the page title as a dbc.Row, to be inserted into the main dbc.Stack of the page."""
    return dbc.Row(
        [
            dbc.Col(
                [
                    html.H1(title_str, style={'font-size': '2.2rem'})
                ],
                width=12
            )
        ]
    )
