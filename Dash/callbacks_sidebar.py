import dash

from dash.dependencies import Input, Output, State

import dataframe
import json

from itertools import permutations


def isint(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


def callbacks_for_sidebar(app):
    @app.callback(
        Output(component_id="slider_annees", component_property="marks"),
        Output(component_id="slider_annees", component_property="max"),
        Output(component_id="slider_annees", component_property="value"),
        Input("output-data-upload", "children"),
    )
    def update_selection_annees(_):
        marks = {}
        i = 0
        column_names = dataframe.df.columns.tolist()
        for name in column_names:
            if isint(name.split("/")[0]):
                marks[i] = {"label": name}
                i += 1
        return marks, len(marks) - 1, [0, len(marks) - 1]

    @app.callback(
        Output(component_id="niveaux_filieres_dd", component_property="options"),
        Output(component_id="niveaux_filieres_dd", component_property="value"),
        Input("slider_annees", "value"),
        Input("select-all-niveaux", "n_clicks"),
        State("slider_annees", "marks"),
        State("niveaux_filieres_dd", "options"),
    )
    def update_dd_niveaux_filieres(value, select_all, list_dict_annees, previous_state):
        ctx = dash.callback_context

        # pas encore triggered
        if not ctx.triggered:
            return [], []
        # triggered par le bouton 'Selectionner tout'
        elif ctx.triggered[0]["prop_id"] == "select-all-niveaux.n_clicks":
            return previous_state, sorted(
                [dict_filliere["label"] for dict_filliere in previous_state]
            )

        # Cas classique
        annees = []
        for key in range(value[0], value[1] + 1):
            annees.append(list_dict_annees[str(key)]["label"])

        niveaux = []
        niveaux_trouves = []
        for index_row, row in dataframe.df[annees].iterrows():
            for index_col, cell in row.iteritems():
                niveau = cell.split(" ")[0]
                if niveau != "Hors" and niveau not in niveaux_trouves:
                    niveaux.append({"label": niveau, "value": niveau})
                    niveaux_trouves.append(niveau)
        return (sorted(niveaux, key=lambda dictionary: dictionary["label"]), [])

    @app.callback(
        Output(component_id="filieres_dd", component_property="options"),
        Output(component_id="filieres_dd", component_property="value"),
        Input("niveaux_filieres_dd", "value"),
        Input("select-all-filieres", "n_clicks"),
        State("slider_annees", "value"),
        State("slider_annees", "marks"),
        State("filieres_dd", "options"),
    )
    def update_dd_filieres(
        niveaux, select_all, value, list_dict_annees, previous_state
    ):
        ctx = dash.callback_context

        # pas encore triggered
        if not ctx.triggered:
            return [], []

        # triggered par le bouton 'Selectionner tout'
        elif ctx.triggered[0]["prop_id"] == "select-all-filieres.n_clicks":
            return previous_state, sorted(
                [dict_filliere["label"] for dict_filliere in previous_state]
            )

        # Cas classique
        annees = []
        for key in range(value[0], value[1] + 1):
            annees.append(list_dict_annees[str(key)]["label"])

        filieres = []
        filieres_trouvees = []
        for index_row, row in dataframe.df[annees].iterrows():
            for index_col, cell in row.iteritems():
                cellule = cell.split(" ")
                if len(cellule) > 1 and (cellule[0] in niveaux or niveaux == []):
                    filiere = cellule[1]
                    if filiere not in filieres_trouvees:
                        filieres.append({"label": filiere, "value": filiere})
                        filieres_trouvees.append(filiere)

        return sorted(filieres, key=lambda dictionary: dictionary["label"]), []

    @app.callback(
        Output(component_id="annee_dd", component_property="options"),
        Input("filieres_dd", "value"),
        State("niveaux_filieres_dd", "value"),
        State("slider_annees", "value"),
        State("slider_annees", "marks"),
    )
    def update_dd_annee(fillieres, niveaux, value, list_dict_annees):
        ctx = dash.callback_context

        # pas encore triggered
        if not ctx.triggered:
            return []

        # Cas classique
        annees = []
        for key in range(value[0], value[1] + 1):
            annees.append(list_dict_annees[str(key)]["label"])

        combinations_fillieres_et_niveau = [
            f"{niveau} {filliere}" for niveau in niveaux for filliere in fillieres
        ]

        annees_communes = []
        for annee in annees:
            column = dataframe.df[annee]

            combinaisons_trouvees = [
                False for _ in range(len(combinations_fillieres_et_niveau))
            ]
            for i, combination in enumerate(combinations_fillieres_et_niveau):
                for _, elem in column.iteritems():
                    if combination in elem and not combinaisons_trouvees[i]:
                        combinaisons_trouvees[i] = True
            if all(combinaisons_trouvees):
                annees_communes.append({"label": annee, "value": annee})

        return sorted(annees_communes, key=lambda dictionary: dictionary["label"])

    @app.callback(
        Output("diplome_dd_div", "style"),
        Input("options_sidebar", "value"),
    )
    def update_diplome_to_color(options_sidebar):
        if "multi-diplome" not in options_sidebar:
            return {}
        else:
            return {"display": "none"}
