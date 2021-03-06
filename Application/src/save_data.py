import os


def sauvegarder_data(pdf_file_name,
                     df_complet,
                     output_path="Fichiers_csv_output"):
    # Sauvegarde les données d'un dataframe (représentant les données d'un
    # unique PV) dans un fichier csv dans le dossier "output_path"
    csv_file_name = pdf_file_name.split(".")
    csv_file_name[-1] = "csv"
    csv_file_name = ".".join(csv_file_name)
    df_complet.to_csv(os.path.join(output_path, csv_file_name),
                      sep=";",
                      index_label="num_etudiant")


def deplacer_pdf(
    pdf_file_name,
    erreur=False,
    input_path="Fichiers_pdf_input",
    fichier_traite_path="Fichiers_pdf_traites",
    fichier_erreur_path="Fichiers_pdf_erreur",
):
    # Déplace un ficher dans un autre dossier. Utilisé pour déplacer les pdf
    # dans les dossiers traités ou ceux qui ont causé une erreur
    if not erreur:
        os.replace(
            os.path.join(input_path, pdf_file_name),
            os.path.join(fichier_traite_path, pdf_file_name),
        )
    else:
        os.replace(
            os.path.join(input_path, pdf_file_name),
            os.path.join(fichier_erreur_path, pdf_file_name),
        )
