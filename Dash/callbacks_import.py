import dash
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

import base64
import pandas as pd
import io
import dash_table

import dataframe


def parse_contents(contents, filename, date):
    # récupère le contenu d'un fichier csv et affiche un appercu
    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    try:
        if "csv" in filename:
            # Assume that the user uploaded a CSV file
            global df
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")), sep=";")
            dataframe.initialize(df)

    except Exception as e:
        return html.Div(["Une erreur est survenue lors de la lecture de ce fichier !"])

    return html.Div(
        [
            html.Hr(),
            "Lecture du fichier ",
            html.B(filename),
            html.Br(),
            html.Br(),
            f"Aperçu des données :",
            dash_table.DataTable(
                data=df.head().to_dict("records"),
                columns=[{"name": i, "id": i} for i in df.columns],
                style_cell_conditional=[
                    {"if": {"column_id": c}, "textAlign": "center"} for c in df.columns
                ],
                style_data_conditional=[
                    {
                        "if": {"row_index": "odd"},
                        "backgroundColor": "#F5F5F6",
                    }
                ],
                style_header={
                    "backgroundColor": "#BDC0BF",
                    "fontWeight": "bold",
                },
                style_cell={"fontSize": "0.75em"},
            ),
        ]
    )


def callbacks_for_import(app):
    @app.callback(
        Output("output-data-upload", "children"),
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
        State("upload-data", "last_modified"),
    )
    def update_output(content, filename, date):
        if content is not None:
            children = [parse_contents(content, filename, date)]
            return children
