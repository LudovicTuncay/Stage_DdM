import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import base64
import pandas as pd
import io
import dash_table

import plotly.express as px

from callbacks_import import callbacks_for_import
from callbacks_sidebar import callbacks_for_sidebar
from callbacks_errors import callbacks_for_errors
from callbacks_graphiques import callbacks_for_graphiques

import dataframe


# Ce fichier s'occupe de la structure du dashboard, d'initialiser l'application
# et de lancer le serveur local

# the style arguments for the sidebar.
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    # "bottom": 0,
    "height": "100%",
    "width": "30%",
    "padding": "20px 10px",
    "background-color": "#f8f9fa",
    "overflow-y": "scroll",
}

# the style arguments for the main content page.
CONTENT_STYLE = {"margin-left": "35%", "margin-right": "5%", "padding": "20px 10p"}

TEXT_STYLE = {"textAlign": "center", "color": "#333333"}

CARD_TEXT_STYLE = {"textAlign": "center", "color": "#555555"}

SELECT_ALL_BUTTON_STYLE = {
    "height": "30px",
    "padding": "0 15px",
    "color": "#0269D9",
    "font-size": "12px",
    "line-height": "30px",
    "background-color": "transparent",
    "border-radius": "5px",
    "border-color": "#0269D9",
    "border": "1px solid #bbb",
    "box-sizing": "border-box",
}

controls = html.Div(
    [
        html.P("Fenêtre de temps étudiée :"),
        dcc.RangeSlider(
            id="slider_annees",
            step=None,
            min=0,
            max=0,
            marks={},
        ),
        html.Hr(),
        html.P("Selection des filières à étudier :"),
        # html.Hr(),
        # html.P("Niveaux des filières", style={"textAlign": "center"}),
        dcc.Dropdown(
            id="niveaux_filieres_dd",
            options=[],
            value=[],
            multi=True,
            placeholder="Selectionner un ou plusieurs niveaux",
        ),
        dbc.Button(
            "Selectionner tout",
            id="select-all-niveaux",
            outline=True,
            color="primary",
            size="sm",
        ),
        html.Br(),
        html.Br(),
        # html.Hr(),
        # html.P("Fillières *", style={"textAlign": "center"}),
        dcc.Dropdown(
            id="filieres_dd",
            options=[],
            value=[],
            multi=True,
            placeholder="Selectionner une ou plusieurs fillières (obligatoire)",
        ),
        dbc.Button(
            "Selectionner tout",
            id="select-all-filieres",
            outline=True,
            color="primary",
            size="sm",
        ),
        html.Br(),
        html.Br(),
        # html.Hr(),
        dcc.Dropdown(
            id="annee_dd",
            placeholder="Forcer une année de présence dans les fillières",
        ),
        # html.Br(),
        # html.P("* : paramètre obligatoire", style={"font-size": ".5em"}),
        html.Hr(),
        html.P("Options :"),
        dcc.Checklist(
            id="options_sidebar",
            options=[
                {"label": "Afficher les sessions", "value": "afficher_session"},
                # {
                #     "label": "Grouper par diplome pour la selection",
                #     "value": "multi-diplome",
                # },
                {
                    "label": "Colorer tous les différents diplômes",
                    "value": "multi-diplome",
                },
            ],
            value=[],
            labelStyle={
                "display": "inline-block",
                "marginRight": "20px",
                "marginLeft": "20px",
            },
        ),
        html.Div(
            [
                "Selectionnez le dernier diplôme obtenu à colorer :",
                dcc.Dropdown(
                    id="diplome_dd",
                    options=[
                        {"label": "3LA", "value": "3LA"},
                        {"label": "L1", "value": "L1"},
                        {"label": "L2", "value": "L2"},
                        {"label": "L3", "value": "L3"},
                        {"label": "M1", "value": "M1"},
                        {"label": "M2", "value": "M2"},
                    ],
                    value="M2",
                    clearable=False,
                    multi=False,
                ),
            ],
            id="diplome_dd_div",
            style={"display": "none"},
        ),
        html.Hr(),
        dbc.Alert(
            "Un ou plusieurs paramètre(s) obligatoire(s) n'a (ont) pas été rempli(s).",
            id="alerte_param_manquant",
            dismissable=True,
            is_open=False,
            color="danger",
        ),
        dbc.Button(
            id="bouton_soumettre",
            n_clicks=0,
            children="Submit",
            color="success",
            block=True,
        ),
    ]
)

footer_sidebar = html.Div(
    children=[html.Br(), "Dapartement de Mathématiques - UPS"],
    style={
        "bottom": "0",
        "background-color": "#f8f9fa",
    },
)

sidebar = html.Div(
    [
        html.H3("Paramètres", style=TEXT_STYLE),
        html.Hr(),
        controls,
        footer_sidebar,
    ],
    style=SIDEBAR_STYLE,
)

content_import_donnees = html.Div(
    [
        html.H5("Upload des données de suivi d'étudiants :"),
        dcc.Upload(
            id="upload-data",
            children=html.Div(
                [
                    "Glissez et déposez ou ",
                    html.B([html.A("selectionnez un fichier")]),
                    " au format csv",
                ]
            ),
            style={
                "width": "100%",
                "height": "50px",
                "lineHeight": "50px",
                "borderWidth": "1px",
                "borderRadius": "5px",
                "borderStyle": "solid",
                "textAlign": "center",
                "position": "relative",
                "margin": "10px",
            },
            # Allow multiple files to be uploaded
            multiple=False,
        ),
        html.Div(id="output-data-upload"),
    ]
)

content_graphiques = html.Div(
    [
        # html.H4("Graphique des flux"),
        html.Div(
            children=[],
            id="div_graphique_flux",
            style={"display": "none"},
        ),
    ]
)

content_analyse_stat = html.Div(
    [
        html.H4("Analyse des flux"),
        html.Br(),
    ],
)

footer = html.Footer(
    children=["Réalisé par Ludovic Tuncay"],
    style={
        "position": "fixed",
        "bottom": "0",
        "background-color": "#ffffff",
        "display": "center",
    },
)

content = html.Div(
    [
        html.H1("Analyse et représentation des flux d'étudiants", style=TEXT_STYLE),
        html.Hr(),
        content_import_donnees,
        html.Hr(),
        content_graphiques,
        # html.Hr(),
        # content_analyse_stat,
        html.Hr(),
        # footer,
    ],
    style=CONTENT_STYLE,
)


# on initialise le dashboard
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div([sidebar, content])


# on appelle les callbacks pour les initialiser
callbacks_for_import(app)
callbacks_for_sidebar(app)
callbacks_for_errors(app)
callbacks_for_graphiques(app)


if __name__ == "__main__":
    app.run_server(debug=False, port="8085")
