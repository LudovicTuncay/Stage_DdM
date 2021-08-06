import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import ipywidgets as widgets
from dash.exceptions import PreventUpdate


from collections import Counter

import pandas as pd
import itertools
import re


import plotly.express as px
import plotly.graph_objs as go

import dataframe

import json
import datetime

BLUE = "#5590C0"
GREEN = "#55904A"
YELLOW = "#E3B23C"
GREY = "#CCCCCC"
DARK_BLUE = "#201E50"
PURPLE = "#B370B0"
ORANGE = "#DE541E"

# Le type de fichier lorsqu'on sauvegarde un graphe
file_type = "svg"  # valeurs possibles :  'jpeg', 'png', 'webp', 'svg'

dict_diplome_to_number = {
    "3LA": "1",
    "L1": "2",
    "L2": "3",
    "L3": "4",
    "M1": "5",
    "M2": "6",
}

dict_diplome_num_to_years_needed = {
    "1": 1,
    "2": 1,
    "3": 2,
    "4": 3,
    "5": 4,
    "6": 5,
}

dict_number_to_diplome = {
    "0": "None",
    "1": "3LA",
    "2": "L1",
    "3": "L2",
    "4": "L3",
    "5": "M1",
    "6": "M2",
}

colorscale = [
    GREY,  # aucun diplome
    DARK_BLUE,  # 3LA
    PURPLE,  # L1
    YELLOW,  # L2
    BLUE,  # L3
    ORANGE,  # M1
    GREEN,  # M2
]

discrete_colorscale = {
    "None": GREY,
    "3LA": DARK_BLUE,
    "L1": PURPLE,
    "L2": YELLOW,
    "L3": BLUE,
    "M1": ORANGE,
    "M2": GREEN,
}


fig = None
clicks = 0


def garder_niveau_et_formation(cell):
    return cell.split(" - ")[0]


def diplome_to_number(cell):
    return dict_diplome_to_number.get(cell, "0")


def combinaisons_annees_filieres(niveaux, filieres):
    combinations = []
    if niveaux == []:
        combinations = [f"{filiere}" for filiere in filieres]
    else:
        combinations = [
            f"{niveau} {filiere}" for niveau in niveaux for filiere in filieres
        ]
    return combinations


def creer_graphe(annees, df):
    # On commence a créer le graphe :
    dimensions = []
    for annee in annees:
        dimensions.append({"label": annee, "values": df.loc[:, annee]})

    diplomes_utilises = sorted(Counter(df["diplomes"]).keys())

    custom_colorscale = [colorscale[int(diplome)] for diplome in diplomes_utilises]

    if (
        len(custom_colorscale) <= 1
    ):  # POur régler un problème dont je ne connais pas la cause
        custom_colorscale.insert(0, colorscale[0])

    color = [colorscale[int(diplome)] for diplome in df["diplomes"]]
    parcats = go.Parcats(
        dimensions=dimensions,
        line={
            "color": color,
            "shape": "hspline",
        },
        hoveron="color",
        hoverinfo="probability",
    )
    global fig
    fig = go.Figure(data=[parcats])
    fig.update_layout(title="Graphique des flux d'étudiants")
    # fig.update_layout(clickmode="event")
    # fig.data[0].on_click(show_stats)
    graph = dcc.Graph(
        figure=fig,
        id="graphique_flux",
        config={"toImageButtonOptions": {"format": file_type, "scale": 1}},
    )
    return graph


def creer_legende(df):
    codes_diplomes_trouves = sorted(list(Counter(df["diplomes"]).keys()))

    couleurs_utilisees = [
        colorscale[int(code_diplome)] for code_diplome in codes_diplomes_trouves
    ]

    diplomes_trouves = [
        dict_number_to_diplome[str(code_diplome)]
        for code_diplome in codes_diplomes_trouves
    ]

    legende_couleurs = [
        dbc.Badge(" ", color=couleur, style={"font-size": "25px"})
        for couleur in couleurs_utilisees
    ]

    legende_texte = [
        f" : élèves ayant obtenu un(e) {niveau}"
        if niveau != "None"
        else " : élèves n'ayant pas obtenu de diplome"
        for niveau in diplomes_trouves
    ]

    legende_breaks = [html.Br() for _ in range(len(legende_texte))]

    legende = [
        ligne_legende
        for zipped in zip(legende_couleurs, legende_texte, legende_breaks)
        for ligne_legende in zipped
    ]
    legende += [
        html.Br(),
        html.P(
            "Les diplomes affichés correspondent au dernier diplome obtenu par l'étudiant au cours de sa scolarité entière (et non pas sur les années sélectionnées).",
            style={"font-size": ".7em"},
        ),
        html.P(
            "De plus, il se peut que les informations affichées soient inexactes par manque de données à la source.",
            style={"font-size": ".7em"},
        ),
    ]
    return dbc.Toast(
        children=legende,
        header="Légende :",
        dismissable=False,
        style={"maxWidth": "100%"},
    )


def garder_eleves_concernes(df, annee_commune, annees, combinations):
    masque = []
    if annee_commune in annees:
        colonne = df[annee_commune].tolist()
        masque = []
        for cell in colonne:
            to_append = False
            for combination in combinations:
                if re.search(rf"\b{combination}\b", cell):
                    to_append = True
                    break
            masque.append(to_append)
    # Ici on ne force pas la présence des élèves, on ne les fait apparaitre
    # que si ils ont été au moins une fois dans les formations spécifiées.
    else:
        for _, row in df.iterrows():
            to_append = False
            for cell in row.tolist():
                for combination in combinations:
                    if re.search(rf"\b{combination}\b", cell):
                        to_append = True
                        break
                if to_append:
                    break
            masque.append(to_append)
    return df[masque]


def create_selection_mode():
    return html.Div(
        children=[
            "Sélection des élèves par : ",
            dbc.ButtonGroup(
                [
                    dbc.Button("formation", id="categorie_boutton"),
                    dbc.Button("couleur", id="couleur_boutton", active=True),
                    dbc.Button("année", id="dimension_boutton"),
                ]
            ),
        ]
    )


def graphe_mutlidiplome(selection_etudiant):
    moyennes = selection_etudiant["moyenne"]

    annees_dernier_diplome = selection_etudiant["annee_valid_diplome"].to_list()
    annees_dernier_diplome = [
        int(annee_dernier_diplome.split("/")[-1])
        if annee_dernier_diplome != "None"
        else datetime.datetime.now().year
        for annee_dernier_diplome in annees_dernier_diplome
    ]
    num_etudiants = selection_etudiant["num_etudiant"].to_list()
    annees_arrivee = [
        int("20" + num_etudiant[1:3])
        if num_etudiant[0] == "2"
        else int("19" + num_etudiant[:2])  # num etudiant de la forme 97... par exemple
        for num_etudiant in num_etudiants
    ]
    temps_passe = [
        annees_dernier_diplome[i] - annees_arrivee[i]
        for i in range(len(annees_arrivee))
    ]

    dernier_diplome_num = selection_etudiant["diplomes"]
    dernier_diplome = [dict_number_to_diplome[number] for number in dernier_diplome_num]

    data = pd.DataFrame(
        data={
            "diplome": dernier_diplome,
            "moyenne": moyennes,
            "annees_ecoulees": temps_passe,
        }
    )

    data.dropna()
    data = data[data["moyenne"] != "None"]
    data = data[data["annees_ecoulees"] != "None"]

    data["moyenne"] = data["moyenne"].astype(float)

    graph = px.scatter(
        data,
        x="moyenne",
        y="annees_ecoulees",
        color="diplome",
        labels={
            "moyenne": "Moyenne des notes obtenues durant le parcours scolaire",
            "annees_ecoulees": "Années écoulées depuis la première<br>inscription à l'université",
            "diplome": "Dernier diplome obtenu :",
        },
        marginal_x="histogram",
        marginal_y="histogram",
        color_discrete_map=discrete_colorscale,
    )

    return graph


def infos_selection_par_filiere(
    selection_etudiant,
    nb_etudiants_par_diplome,
    prop_diplome,
    nb_etudiants_selectionnes,
    dfs_par_diplomes,
):
    new_infos = [
        html.Div(
            [
                html.P(
                    f"{nb_etudiants_par_diplome[0]} élèves ({prop_diplome[0]:.0f}% des {nb_etudiants_selectionnes}) dans la selection n'ont pas eu de diplome (parmis ceux affichés)"
                ),
            ]
        )
    ]
    new_infos += [
        html.Div(
            [
                html.P(
                    f"{nb_etudiants_par_diplome[i]} élèves ({prop_diplome[i]:.0f}% des {nb_etudiants_selectionnes}) dans la selection ont obtenu leur {dict_number_to_diplome[str(i)]}"
                )
                for i in range(len(dfs_par_diplomes))
                if (nb_etudiants_par_diplome[i] != 0 and i != 0)
            ]
            + [dcc.Graph(figure=graphe_mutlidiplome(selection_etudiant))]
        )
    ]
    return new_infos


def create_graph_selection_diplome(selection_etudiant, annees_arrivee, diplome):
    annees_dernier_diplome = selection_etudiant["annee_valid_diplome"].to_list()
    annees_dernier_diplome = [
        int(annee_dernier_diplome.split("/")[-1])
        for annee_dernier_diplome in annees_dernier_diplome
    ]
    temps_passe = [
        annees_dernier_diplome[i] - annees_arrivee[i]
        for i in range(len(annees_arrivee))
    ]
    temps_passe_theorique = dict_diplome_num_to_years_needed[diplome]

    comptes_temps_passe = dict(Counter(temps_passe))

    X = sorted(comptes_temps_passe.keys())

    infos_graphe = []

    # Pour les étudiants qui ont validé leur diplome plus vite que prévu
    trace_x_blue = [x for x in X if x < temps_passe_theorique]
    trace_y_blue = [comptes_temps_passe[x] for x in trace_x_blue]
    hovertemplate_blue = (
        "<br>Moins que prévu. Surement car l'étudiant arrive d'un autre établissement."
    )
    infos_graphe.append(
        (trace_x_blue, trace_y_blue, hovertemplate_blue, BLUE, "Temps plus faible")
    )

    # POur les étudiants qui ont validé leur diplome dans le temps
    trace_x_green = [x for x in X if x == temps_passe_theorique]
    trace_y_green = [comptes_temps_passe[x] for x in trace_x_green]
    hovertemplate_green = "<br>C'est le temps prévu pour ce diplome. Surement car l'étudiant n'a jamais redoublé."
    infos_graphe.append(
        (trace_x_green, trace_y_green, hovertemplate_green, GREEN, "Temps prévu")
    )

    trace_x_yellow = [x for x in X if x == temps_passe_theorique + 1]
    trace_y_yellow = [comptes_temps_passe[x] for x in trace_x_yellow]
    hovertemplate_yellow = "<br>C'est plus que prévu. Surement car l'étudiant a redoublé une fois ou s'est réorienté."
    infos_graphe.append(
        (
            trace_x_yellow,
            trace_y_yellow,
            hovertemplate_yellow,
            YELLOW,
            "Temps légèrement supérieur",
        )
    )

    trace_x_orange = [x for x in X if x > temps_passe_theorique + 1]
    trace_y_orange = [comptes_temps_passe[x] for x in trace_x_orange]
    hovertemplate_orange = "<br>C'est plus que prévu. Surement car l'étudiant a redoublé plusieurs fois ou s'est réorienté."

    infos_graphe.append(
        (
            trace_x_orange,
            trace_y_orange,
            hovertemplate_orange,
            ORANGE,
            "Temps supérieur",
        )
    )

    graph = go.Figure()
    for info_graphe in infos_graphe:
        graph.add_trace(
            go.Bar(
                x=info_graphe[0],
                y=info_graphe[1],
                hovertemplate="Il a fallu %{x} années à %{y} étudiants pour valider leur"
                + f" {dict_number_to_diplome[diplome]}."
                + info_graphe[2]
                + "<extra></extra>",
                marker_color=info_graphe[3],
                showlegend=True,
                name=info_graphe[4],
            )
        )
    graph.update_traces(texttemplate="%{y}", textposition="outside")
    graph.update_layout(
        title=f"Temps nécéssaire aux étudiant pour valider leur {dict_number_to_diplome[diplome]}",
        yaxis=dict(title="Nombre d'étudiants"),
        xaxis=dict(title="Nombre d'années depuis l'insciption à l'Université"),
        legend=dict(title="Légende :"),
    )
    return graph


def create_graph_selection_no_diplome(selection_etudiant, annees_arrivee):

    cette_annee = datetime.datetime.now().year
    temps_passe_a_fac = [
        cette_annee - annees_arrivee[i] for i in range(len(annees_arrivee))
    ]
    data = Counter(temps_passe_a_fac)

    x = list(data.keys())
    y = list(data.values())

    graph = go.Figure(
        go.Bar(
            x=x,
            y=y,
            hovertemplate="Ces %{y} étudiants se sont inscrits il y a %{x} années"
            + f"<br>À ce jour, ils n'ont toujours pas de diplome (parmis ceux affichés)."
            + "<extra></extra>",
        )
    )
    graph.update_traces(texttemplate="%{y}", textposition="outside")
    graph.update_layout(
        title=f"Répartition du nombre d'années écoulées depuis l'inscription des étudiants<br>n'ayant pas obtenu de diplome (parmis ceux affichés)",
        yaxis=dict(title="Nombre d'étudiants"),
        xaxis=dict(title="Nombre d'années depuis l'insciption à l'Université"),
    )

    return graph


def infos_selection_par_diplome(selection_etudiant):

    num_etudiants = selection_etudiant["num_etudiant"].to_list()
    annees_arrivee = [
        int("20" + num_etudiant[1:3])
        if num_etudiant[0] == "2"
        else int("19" + num_etudiant[:2])  # num etudiant de la forme 97...
        for num_etudiant in num_etudiants
    ]
    # On vérifie que les étudiants possèdent bien un diplome
    diplome = selection_etudiant["diplomes"].to_list()[0]
    if diplome != "0":
        graph = create_graph_selection_diplome(
            selection_etudiant, annees_arrivee, diplome
        )

    # Si les étudiants n'ont pas de diplome, on ne peut pas afficher les infos
    # sur le temps passé pour obtenir ce même diplome. Donc on affiche un
    # histogramme des années d'arrivée à la fac.
    else:
        graph = create_graph_selection_no_diplome(selection_etudiant, annees_arrivee)

    return [
        dcc.Graph(
            figure=graph,
            config={"toImageButtonOptions": {"format": file_type, "scale": 1}},
        )
    ]


def infos_selection_par_annee(
    selection_etudiant,
    nb_etudiants_par_diplome,
    prop_diplome,
    nb_etudiants_selectionnes,
    dfs_par_diplomes,
):
    new_infos = [
        html.Div(
            [
                html.P(
                    f"{nb_etudiants_par_diplome[0]} élèves ({prop_diplome[0]:.0f}% des {nb_etudiants_selectionnes}) n'ont pas eu de diplome (parmis ceux affichés)"
                ),
            ]
        )
    ]
    new_infos += [
        html.Div(
            [
                html.P(
                    f"{nb_etudiants_par_diplome[i]} élèves ({prop_diplome[i]:.0f}% des {nb_etudiants_selectionnes}) ont obtenu leur {dict_number_to_diplome[str(i)]}"
                )
                for i in range(len(dfs_par_diplomes))
                if (nb_etudiants_par_diplome[i] != 0 and i != 0)
            ]
        )
    ]
    new_infos += [dcc.Graph(figure=graphe_mutlidiplome(selection_etudiant))]
    return new_infos


def callbacks_for_graphiques(app):
    @app.callback(
        Output("graphique_flux", "figure"),
        Output("categorie_boutton", "active"),
        Output("couleur_boutton", "active"),
        Output("dimension_boutton", "active"),
        Input("categorie_boutton", "n_clicks"),
        Input("couleur_boutton", "n_clicks"),
        Input("dimension_boutton", "n_clicks"),
    )
    def toggle_switch(categorie, couleur, dimension):
        ctx = dash.callback_context

        if not ctx.triggered:
            raise PreventUpdate
        else:
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        new_fig = fig

        if not any([categorie, couleur, dimension]):
            new_fig.data[0].hoveron = "color"
            return new_fig, False, True, False
        elif button_id == "categorie_boutton":
            new_fig.data[0].hoveron = "category"
            return new_fig, True, False, False
        elif button_id == "couleur_boutton":
            new_fig.data[0].hoveron = "color"
            return new_fig, False, True, False
        elif button_id == "dimension_boutton":
            new_fig.data[0].hoveron = "dimension"
            return new_fig, False, False, True

    @app.callback(
        Output(component_id="div_graphique_flux", component_property="children"),
        Output(component_id="div_graphique_flux", component_property="style"),
        Input("bouton_soumettre", "n_clicks"),
        State("alerte_param_manquant", "is_open"),
        State("slider_annees", "value"),
        State("slider_annees", "marks"),
        State("niveaux_filieres_dd", "value"),
        State("filieres_dd", "value"),
        State("annee_dd", "value"),
        State("options_sidebar", "value"),
        State("diplome_dd", "value"),
        prevent_initial_call=True,
    )
    def update_selection_annees(
        clicks_bouton,
        param_manquant,
        index_annees,
        list_dict_annees,
        niveaux,
        filieres,
        annee_commune,
        options,
        diplome_to_color,
    ):
        # Si il manque des paramètres, on fait bien attention de ne pas tracer
        # le graphe.
        if param_manquant:
            return [], {"display": "none"}

        annees = []
        for key in range(index_annees[0], index_annees[1] + 1):
            annees.append(list_dict_annees[str(key)]["label"])

        df = dataframe.df[annees + ["num_etudiant"]].copy()
        df = df.astype(str)
        # print(df.dtypes)

        diplomes = dataframe.df["last_diplome_valide"].tolist()
        annees_valid = dataframe.df["last_annee_validee"].tolist()

        if "afficher_session" not in options:
            df = df.applymap(garder_niveau_et_formation)

        if "multi-diplome" in options:
            diplomes = [diplome_to_number(diplome) for diplome in diplomes]
        else:
            diplomes = [
                diplome_to_number(diplome_to_color)
                # Changer par >= si on considère que les gens ayant un M2, ont une L3 (par exemple).
                # Attention, cela change les graphe pour avoir le temps nécécaire pour obtenir ce diplome. En effet, ils seront noté comme ayant obtenu le diplome plus tard qu'en réalité
                if diplome == diplome_to_color else "0"
                for diplome in diplomes
            ]

        df["diplomes"] = diplomes
        df["annee_valid_diplome"] = annees_valid
        df["moyenne"] = dataframe.df["moyenne"]

        # On calcule les combinaisons niveau/fillière par exemple si
        # l'utilisateur a selectionné "L3" et "M1" en années et "SID" et "E" en
        # fillières, combinaisons sera égal à :
        # ["L3 SID", "M1 SID", "L3 E", "M1 E"]
        combinations = combinaisons_annees_filieres(niveaux, filieres)
        # Si c'est spécifié dans "annee_commune", on  force la présence des
        # élèves une certaine année pour les formations selectionnées.
        df = garder_eleves_concernes(df, annee_commune, annees, combinations)
        dataframe.initialize_df_to_study(df)

        # On commence a créer le graphe :
        graph = creer_graphe(annees, df)

        selection_mode = create_selection_mode()
        # La légende
        legende = creer_legende(df)

        return (
            [selection_mode, graph, html.Div(id="infos_clicked"), legende],
            {},
        )

    @app.callback(
        Output("infos_clicked", "children"),
        Input("graphique_flux", "clickData"),
        State("categorie_boutton", "active"),
        State("couleur_boutton", "active"),
        State("dimension_boutton", "active"),
    )
    def selection_etudiant_card(
        click_data, categorie_boutton, couleur_boutton, dimension_boutton
    ):

        df_studied = dataframe.df_to_study

        # print(df_studied)
        # Si on selectionne par année, alors on utilise tout le dataframe
        if dimension_boutton:
            selection_etudiant = df_studied
            nb_etudiants_selectionnes = len(df_studied.index)
        # Sinon on utilise les étudiants que clickData nous foruni
        else:
            points = click_data["points"]
            indices = [point["pointNumber"] for point in points]

            selection_etudiant = df_studied.iloc[indices]
            nb_etudiants_selectionnes = len(indices)

        nb_etuiants_tot = len(df_studied.index)

        prop_etudiants_selectionnes = nb_etudiants_selectionnes / nb_etuiants_tot

        dfs_par_diplomes = [
            selection_etudiant[selection_etudiant["diplomes"] == diplome]
            for diplome in dict_number_to_diplome.keys()
        ]

        nb_etudiants_par_diplome = [len(df.index) for df in dfs_par_diplomes]

        prop_diplome = [
            (nb_etudiant_diplome / nb_etudiants_selectionnes) * 100
            for nb_etudiant_diplome in nb_etudiants_par_diplome
        ]

        infos = [
            html.P(
                f"{nb_etudiants_selectionnes} étudiants sélectionnés sur {nb_etuiants_tot} au total ({prop_etudiants_selectionnes*100:.0f}%)."
            ),
        ]

        # selection des élèves par catégorie (formation)
        if categorie_boutton:
            new_infos = infos_selection_par_filiere(
                selection_etudiant,
                nb_etudiants_par_diplome,
                prop_diplome,
                nb_etudiants_selectionnes,
                dfs_par_diplomes,
            )

        # selection des élèves par couleur (diplome)
        elif couleur_boutton:
            new_infos = infos_selection_par_diplome(selection_etudiant)

        # selection des élèves par année (qui au final nous renvoie que les
        # étudiants de la formation qu'on survole)
        else:
            new_infos = infos_selection_par_annee(
                selection_etudiant,
                nb_etudiants_par_diplome,
                prop_diplome,
                nb_etudiants_selectionnes,
                dfs_par_diplomes,
            )
        infos += new_infos

        return dbc.Toast(
            infos,
            header="Informations sur les étudiants sélectionnés :",
            dismissable=True,
            style={"maxWidth": "100%"},
        )
