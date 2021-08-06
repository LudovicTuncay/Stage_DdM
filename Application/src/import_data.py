# Fichier python responsable de l'import des données à partir du fichier pdf

import os  # Pour la manipulation des chemins vers les fichiers
import camelot  # librairie pour lire le fichier pdf et le transformer en liste

# de dataframes. Où chaque dataframe correspond a un tableau
# dans le fichier pdf
from pdfminer.high_level import extract_text, extract_pages
import pandas as pd


# Code de la fonction repris de https://github.com/camelot-dev/camelot/issues/28#issuecomment-509974313
def chunks(liste, chunk_size):
    """
    DESCRIPTION :
        Récupère des morceaux de taille "chunck_size" de la liste données en
        paramètre.
        A chaque fois que la fonction est appellée, elle renvoie le morceau
        suivant.
    ---------------------------------------------------------------------------
    INPUT :
        liste : une liste quelconque
        chunk_size (int) : la taille souhaitée de chaque morceau de la liste.
    OUTPUT :
        une liste de "chunk_size" éléments consécutifs de "liste"
    """
    for index in range(0, len(liste), chunk_size):
        yield liste[index:index + chunk_size]


def trouver_substring(string, substring, nth_occurence=1):
    parties = string.split(substring, nth_occurence + 1)
    if len(parties) <= nth_occurence + 1:
        return -1
    return len(string) - len(parties[-1]) - len(substring)


def get_pages_list(pdf_file_name):
    """
    DESCRIPTION :
        Retourne une liste des numéros de page de notre pdf
    ---------------------------------------------------------------------------
    INPUT :
        pdf_file_name (str) : une chaine de caractère qui correspond au chemin
        vers le fichier pdf.
    OUTPUT :
        une liste d'entier, par exemple pour un pdf de 3 pages la sortie serait
        [1,2,3]
    """
    pages = list(extract_pages(pdf_file_name))
    list_of_page_numbers = list(range(1, len(pages)))
    return list_of_page_numbers


def recuperer_tables_pdf(pdf_file_path):
    """
    DESCRIPTION :
        Récupère l'ensemble des tableaux présent dans un pdf et les
        informations diverses du procès verbal puis les retourne
    ---------------------------------------------------------------------------
    INPUT :
        pdf_file_name (str) : une chaine de caractère qui correspond au chemin
        vers le fichier pdf.
    OUTPUT :
        une liste de dataframe ou chaque dataframe correspond a un tableau dans
        le pdf.
    """

    # Le nombre de page à traiter en une fois
    chunk_size = 3

    pages_list = get_pages_list(pdf_file_path)

    # La liste des morceaux de pages a traiter
    pages_chunks = list(chunks(pages_list, chunk_size))

    # la liste dans laquelle on va trouver les dataframes qui représentent les
    # tableaux du pdf
    list_of_df = []
    for chunk in pages_chunks:

        # les numéros de pages a traiter sur ce passage
        pages_string = str(chunk).replace('[', '').replace(']', '')

        # Les tableaux présent dans ce chunk de pages
        tableaux_dans_chunk = camelot.read_pdf(pdf_file_path,
                                               pages=pages_string,
                                               split_text=True)

        # on ajoute les tableaux dans notre liste de dataframes
        list_of_df += [tableau.df for tableau in tableaux_dans_chunk]
    return list_of_df


def get_niveau_et_formation(texte):
    """
    DESCRIPTION :
        Récupère le niveau et le nom de la formation a partir d'un texte
    ---------------------------------------------------------------------------
    INPUT :
        texte (str) : une chaine de caractère qui contient le niveau et le nom
        de la formation
    OUTPUT :
        un tuple de chaines de charactères. Le premier élément correspond au
        niveau de la formation et le deuxième élément correspond au nom de la
        formation.
    ----------------------------------------------------------------------------
    EXAMPLE :
        IN : "EMD43BS L3 Statistiques et Informatique Décisionnelle"
        OUT : ("L3", "Statistique et Informatique")
    """
    codes_annees = ["L1", "L2", "L3", "M1", "M2"]
    codes_CUPGE = {"1ERE": "L1", "2EME": "L2", "3EME": "L3"}
    texte = texte.split(" ")
    for i, mot in enumerate(texte):
        if mot in codes_CUPGE.keys():
            niveau = codes_CUPGE[mot]
            formation = " ".join(texte[i+2:]).strip()
        elif mot in codes_annees:
            niveau = mot
            formation = " ".join(texte[i+1:]).strip()
    return niveau, formation


def recuperer_infos_pv(pdf_file_path):
    # On récupère le texte d'une des premières pages
    try:
        text = extract_text(pdf_file_path, page_numbers=[2])
    except Exception:
        text = extract_text(pdf_file_path, page_numbers=[1])
    if text == '\x0c':
        raise Exception("page non reconnue (surement une image)")

    useful_info = text.split("\n\n")

    session_trouvee, formation_trouvee = False, False
    for element in useful_info:
        if "Session" in element and not session_trouvee:
            session_et_date = element
            session_trouvee = True
        if "Version" in element and not formation_trouvee:
            niveau_et_formation = element
            formation_trouvee = True
        if session_trouvee and formation_trouvee:
            break
    num_session = session_et_date.split(" ")[1]
    date = session_et_date.split(" ")[-1].split("/")[0]
    niveau, formation = get_niveau_et_formation(niveau_et_formation)
    return date, num_session, niveau, formation


def import_data(pdf_file_path):
    infos_pv = recuperer_infos_pv(pdf_file_path)
    liste_df = recuperer_tables_pdf(pdf_file_path)
    return liste_df, infos_pv
