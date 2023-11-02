"""Main module for the webapp frontend."""
import logging

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[
        dbc.themes.FLATLY,
        dbc.icons.FONT_AWESOME
    ],
    suppress_callback_exceptions=True,
    pages_folder='../pages'
)


def navbar() -> dbc.NavbarSimple:
    """Defines the navigation bar for the webapp."""

    nav_dropdown_style = {'in_navbar': True, 'nav': True, 'align_end': True}
    children = [
        dbc.NavLink(
            ['Homepage\u2002', html.Span(className='fa fa-house')],
            href='/'
        ),
        dbc.DropdownMenu(
            [
                dbc.DropdownMenuItem("View Sensors", href='/sensors'),
                dbc.DropdownMenuItem(
                    "View Data Connectors and Gateways",
                    href='/gateway-data-connectors'
                ),
                dbc.DropdownMenuItem(
                    ["2D Map\u2002", html.Span(className='fa fa-map-location-dot')],
                    href='/sensors/2d'
                )
            ],
            label=['Sensors\u2002', html.Span(className='fa fa-tower-broadcast')],
            **nav_dropdown_style
        ),
        dbc.DropdownMenu(
            [
                dbc.DropdownMenuItem(
                    ["Simulator\u2002", html.Span(className='fa fa-microchip')],
                    href='/hpath'
                ),
                dbc.DropdownMenuItem(
                    ["BIM\u2002", html.Span(className='fa fa-diagram-project')],
                    href='/hpath/bim'
                )
            ],
            label=['Histopatology\u2002', html.Span(className='fa fa-bacteria')],
            **nav_dropdown_style
        ),
        dbc.NavLink(
            ['Documentation\u2002', html.Span(className='fa fa-book-open')],
            href='https://yinchi.github.io/cuh-dashboards/',
            external_link=True,
            target='_blank'
        ),
    ]
    return dbc.NavbarSimple(
        children=children,
        brand='CUH Digital Hospitals Dashboards Demo',
        brand_href='/',
        fluid=True,
        expand='lg',
        class_name='py-1',
        color='primary',
        dark=True,
        id='navbar'
    )


app.layout = dbc.Container(
    [
        dcc.Location(id='location'),
        navbar(),
        html.Div(dash.page_container, className='mt-3 mx-3')
    ],
    fluid=True,
    class_name='dbc m-0 p-0 w-auto',
    style={'max-width': '1600px'}
)

if __name__ == '__main__':
    # Example output:
    # app       20396   Sep 27 22:35:12.127 <message body>
    FORMAT = "%(process)5d   %(asctime)s.%(msecs)03d %(message)s"
    DATE_FORMAT = '%b %d %H:%M:%S'

    formatter = logging.Formatter(fmt=FORMAT, datefmt=DATE_FORMAT)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    app.logger.handlers = [handler]

    app.logger.info("")
    app.logger.info("")
    app.logger.info("================================================")
    app.logger.info("Dash app started/restarted")
    app.logger.info("================================================")
    app.logger.info("")
    app.logger.info("")

    print(dash.get_asset_url('examples/config.xlsx'))
    print(app.server.url_map)
    app.run(host='0.0.0.0', port=3000, debug=True)
