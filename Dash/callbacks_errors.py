from dash.dependencies import Input, Output, State


def callbacks_for_errors(app):
    @app.callback(
        Output(component_id="alerte_param_manquant", component_property="is_open"),
        Input("bouton_soumettre", "n_clicks"),
        State("filieres_dd", "value"),
    )
    # affiche une erreur si on a pas rempli la case
    def show_submit_error_message(n_clicks, fillieres):
        return n_clicks > 0 and fillieres == []
