"""Page for showing results for a single simulation scenario."""
import dash
from dash import html

dash.register_page(
    __name__,
    title='Histopathology: Scenario Results',
    path_template='/hpath/view/single/<scenario_id>'
)


def layout(scenario_id=None):
    """Build the layout to show the given scenario's result.
    """
    # TODO fetch result, if error show error message

    # TODO replicate Lakee's result page?
    return html.Div(
        f"The user requested scenario ID: {scenario_id}."
    )
