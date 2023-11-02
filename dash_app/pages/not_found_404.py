"""Defines the page returned when no other path matches.
See: https://dash.plotly.com/urls#default-and-custom-404."""
import dash
from dash import dcc, html

dash.register_page(__name__)

layout = [
    html.H1("404", style={'font-size': '1.6rem'}),
    dcc.Markdown(
        """\
The page you are looking for was not found.
Either the URL is incorrect or the page has
not yet been implemented. Note that this
website is still under development."""
    ),
    html.Div(
        dcc.Link('Home', href='/')
    )
]
