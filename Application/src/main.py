import os
import sys
import filetype
from multiprocessing import cpu_count
from tqdm.contrib.concurrent import process_map
from import_data import import_data
from traiter_data import premier_traitement, second_traitement, fusionner_liste_df
from save_data import sauvegarder_data, deplacer_pdf


def traiter_pdf(pdf_file_name,
                input_path="Fichiers_pdf_input",
                output_path="Fichiers_csv_output"):
    """
    DESCRIPTION:
        Traite un fichier pdf (procès verbal) du début à la fin et fait
        l'export dans le dossier
    ---------------------------------------------------------------------------
    INPUT:
        pdf_file_name (str) : le nom du pdf que l'on doit traiter
        file_path (str) : le chemin du dossier contenant le fichier pdf
    """
    error_code = 0
    log_file_name = "logfile.txt"
    try:
        # Récupération des données dans une liste. Chaque élément de la liste est
        # un dataframe et chaque dataframe correspond a un tableau du fichier pdf
        # Donc dans notre cas, cela correspond à une page par dataframe.
        # On récupère aussi diverses informations sur le procès verbal (session,
        # année, niveau et domaine)
        liste_df, infos_pv = import_data(
            os.path.join(input_path, pdf_file_name))
        error_code = 1

        # Premier traitement de chaque cellulle pour qu'on puisse faire un
        # traitement plus approfondi et une normalisation des cellulles par la
        # suite.
        liste_df = premier_traitement(liste_df)
        error_code = 2

        # Deuxième traitement des données. On fait en sorte que chaque cellulle
        # soit au même format.
        liste_df = second_traitement(liste_df, infos_pv)
        error_code = 3

        # Fusion des dataframes pour l'export en un seul csv.
        df_complet = fusionner_liste_df(liste_df)
        error_code = 4

        # sauvegarde du dataframe. On garde le nom de base, on change juste
        # l'extension.
        sauvegarder_data(pdf_file_name, df_complet)

        deplacer_pdf(pdf_file_name)

        with open(log_file_name, "a") as log_file:
            log_file.write(
                f"File {pdf_file_name} finished without any error.\n")
    except Exception as e:

        # deplacer_pdf(pdf_file_name, erreur=True)

        with open(log_file_name, "a") as log_file:
            log_file.write(
                f"ERROR : {pdf_file_name} - code : {error_code} - error message : {str(e)}\n"
            )


def is_pdf_file(file):
    """
    DESCRIPTION:
        vérifie qu'un fichier est un pdf a partir de son nom de fichier.
    ---------------------------------------------------------------------------
    INPUT:
        file (str) : le nom du fichier
    OUTPUT:
        Booléen : True si le fichier est un pdf, False sinon
    """
    kind = filetype.guess(file)
    if kind is None:
        return False
    return kind.extension == "pdf"


if __name__ == "__main__":
    # On change le directory pour avoir accès aux fichiers en input
    os.chdir(os.path.dirname(sys.path[0]))
    # cpu_count compte le nombre de threads du processeur pour pouvoir traiter
    # plusieurs fichiers pdf en une fois
    available_CPUs = max(1, cpu_count() - 1)

    with open("logfile.txt", "w") as log_file:
        log_file.write("Logging content :\n")

    input_path = "Fichiers_pdf_input"

    input_files = [
        f for f in os.listdir(input_path)
        if is_pdf_file(os.path.join(input_path, f))
    ]

    process_map(traiter_pdf,
                input_files,
                max_workers=available_CPUs,
                desc="Fichiers traités ")
