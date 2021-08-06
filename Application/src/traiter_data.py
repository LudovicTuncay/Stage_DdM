import unicodedata
import pandas as pd
from tabulate import tabulate

dico_matieres = {}
# format infos_pv :
# [année session (XXXX/XXXX+1), numero session, Niveau (L1, L2, ...),
#  formation (Mathématiques, Informatique, MAPI3, ...)]
infos_pv = ["", "", "", "", ""]

nb_etud = 10
################################################################################

###############################################
# Fonctions nécéssaires au premier traitement #
###############################################


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def strip_accent(text):
    """
    DESCRIPTION :
        Enlève les accents présents dans un texte
    ----------------------------------------------------------------------------
    INPUT :
        text (str) : une chaine de charactères
    OUTPUT :
        la chaine de charactères sans les accents
    """
    text = unicodedata.normalize("NFD", text)
    text = text.encode("ascii", "ignore")
    text = text.decode("utf-8")
    return text


def normaliser(cellulle):
    """
    DESCRIPTION :
        Normalise le texte d'une cellulle.
    ----------------------------------------------------------------------------
    INPUT :
        cellulle (str) : Le contenu de la cellulle que l'on doit traiter
    OUTPUT :
        Une liste de chaine de charactères, ou chaque élément est en minuscules
        et n'a plus d'accent.
    """
    new_cell = cellulle.lower()  # mets tout en minuscule
    new_cell = new_cell.split("\n")  # transforme en liste
    # enlève les espaces en trop et elève les accents
    new_cell = [strip_accent(string.strip()) for string in new_cell]
    return new_cell


def nommer_colonnes(tables):
    """
    DESCRIPTION :
        Nomme les colonnes des dataframes d'un procès-verbal
    ----------------------------------------------------------------------------
    INPUT :
        tables (list[df]) : une liste de dataframes qui représentent les tables
        dans un procès verbal
    OUTPUT :
        une liste des df ou les colonnes ont été nommées correctement (code des
        matières)
    """
    nouvelles_tables = tables.copy()
    for i, table in enumerate(tables):
        nouvelle_table = table.copy()
        nouveau_header = [
            cell[0].split(" ")[0] for cell in nouvelle_table.iloc[0]
        ]
        # On enlève la première ligne qui ne contient pas d'élève
        nouvelle_table = nouvelle_table[1:]
        # On nomme les conolles avec la liste qu'on a créé.
        nouvelle_table.columns = nouveau_header

        nouvelles_tables[i] = nouvelle_table
    return nouvelles_tables


def creer_dico_matieres(row, dico):
    """
    DESCRIPTION :
       ajoute des matières aux dictionnaire de correspondance code->nom.
    ----------------------------------------------------------------------------
    INPUT :
        row : La ligne du dataframe qui contient les noms de cours et leur code
    OUTPUT :
        le dictionnaire mis à jour avec les nouveaux cours
    """
    for cours in row:
        if len(cours) > 2:
            if len(cours[-2]) <= 2 and not isfloat(cours[-2]):
                nom_cours = " ".join(cours[1:-2])
                nom_cours += cours[-2]
                dico[cours[0]] = nom_cours
            else:
                dico[cours[0]] = " ".join(cours[1:-1])
    return dico


def premier_traitement(liste_df):
    """
    DESCRIPTION :
        Réalise le premier traitement des dataframes d'un procès verbal. La
        fonction en profite pour remplir le dictionnaire des matières.
    ----------------------------------------------------------------------------
    INPUT :
        liste_df (list[df]) : une liste de dataframes qui représentent les
        tables dans un procès verbal
    OUTPUT :
        une liste des df ou les colonnes ont été nommées correctement (code des
        matières), ou le texte dans les cellulles a été normalisé.
    """
    # On normalise les cellulles des tableaux
    # print(liste_df[0])
    liste_df_normalisee = [df.applymap(normaliser) for df in liste_df]
    # print(liste_df[0])
    # On utilise la varaible globale dico_matieres
    global dico_matieres
    # On remplit le dictionnaire
    for df in liste_df_normalisee:
        dico_matieres = creer_dico_matieres(df.iloc[0], dico_matieres)
    # on renomme les colonnes
    liste_df_nommee = nommer_colonnes(liste_df_normalisee)
    return liste_df_nommee


################################################################################

##############################################
# Fonctions nécéssaires au second traitement #
##############################################

# infos_pv de la forme [annee, session_num, niveau]
code_obtention_pv = ("adm", "def", "cmp", "vac", "aj", "adj", "cms", "reo",
                     "ajac")
code_reussite = ("adm", "cmp", "adj", "vac", "ajac")
mention_pv = ("p", "ab", "b", "tb")


def isfloat(value):
    """
    DESCRIPTION :
       Vérifie qu'une chaine de charactère peut etre transfomée en float
    ----------------------------------------------------------------------------
    INPUT :
        value (str) : la chaine à tester
    OUTPUT :
        un booléen : True si la chaine peut etre convertie en float et False 
        sinon
    """
    try:
        float(value)
        return True
    except ValueError:
        return False


def est_un_semestre(col_name):
    """
    DESCRIPTION :
       Vérifie que la colonne est un semestre
    ----------------------------------------------------------------------------
    INPUT :
        col_name (str) : le nom de la colonne
    OUTPUT :
        un booléen : True si la colonne est un semestre et False sinon
    """
    return col_name[-1] == "s"


def notes_possibles(
        case):  # Fonctions qui retourne les valeurs pouvant être une note
    liste = []
    for elem in case:
        for splitter in elem.split(" "):
            # attention à true et false
            if isfloat(splitter
                       ) and float(splitter) >= 0 and float(splitter) <= 20:
                # Tout nombre entre 0 et 20 est une note potentielle
                liste.append(float(splitter))
    return liste


# Fonctions qui retourne les valeurs pouvant correspondre aux crédits
def credits_possibles(case):
    liste = []
    for elem in case:
        if isfloat(elem) and (float(elem) == 3 or float(elem) == 6 or
                              (float(elem) > 20 and float(elem) % 3 == 0)):
            # 3,6, 30, 60 ou 120  peuvent être les crédits
            liste.append(int(float(elem)))
    return liste


def mention(case):  # fonction pour obtenir la mention d'une case
    for elem in case:
        for splitter in elem.split(" "):
            if splitter in mention_pv:
                return splitter
        for splitter in elem.split("/"):
            if splitter in mention_pv:
                return splitter
    return None


def code_obtention(
        case):  # fonction pour obtenir le code d'obtention d'une case
    for elem in case:
        for splitter in elem.split(" "):
            if splitter in code_obtention_pv:
                return splitter
        for splitter in elem.split("/"):
            if splitter in code_obtention_pv:
                return splitter
    return None


def note(case, semestre: bool):  # fonction pour obtenir la note d'une case
    liste_notes = notes_possibles(case)
    if len(liste_notes) > 1:  # il y a la note et crédit ou points jury
        return max(liste_notes)
    elif len(liste_notes) == 0:
        return None
    elif "vac" in case and len(case) == 3:
        return None
    elif semestre:
        return liste_notes[0]
    else:
        return liste_notes[0]


def credit_cours(case):  # trouve les crédits de cours possibles dans la case
    liste_credits = credits_possibles(case)
    if (len(liste_credits) == 0 or len(case) == 1 or "def" in case
            or "aj" in case or "cmp" in case):
        return None
    elif max(liste_credits) == 30:
        return 30
    elif ("vac" in case or "adm" in case or "u adm" in case or "adj" in case
          or case[0][0] == "u" or case[0][0] == "/"):
        return liste_credits[-1]
    elif len(case) == 3:
        return min(liste_credits)
    else:
        return None


def points_jury(case):  # Trouve les points jury possibles dans la case
    liste_notes = notes_possibles(case)
    if len(liste_notes) < 2:
        return None
    elif min(liste_notes) < 1:
        return min(liste_notes)
    else:
        return None


def date_session(case, reussi: bool):
    for elem in case:
        if len(elem) > 3 and elem[-2] == "/":
            return elem[:4], elem[5:]
    if reussi:
        return infos_pv[0], infos_pv[1]
    return None, None


def garder_infos_utiles(cellulle):
    infos_utiles = []
    a_rejeter = [
        "note/pt. jury",
        "res /credits",
        "mention",
        "an/ses",
        "option,fr",
        "ex / es1",
        "rang / es2",
        "note max",
        "note min",
        "note moy",
        "ecart type",
        "moy - écart type",
    ]

    for element in cellulle:
        if element not in a_rejeter:
            infos_utiles.append(element)
    return infos_utiles


def traiter_identification(cell):
    # Une cellulle normale d'indentification d'un étudiant est de longueur 4
    # Lorsqu'elle fait plus, c'est qu'elle est soit polluée par la colonne
    # adjascente, soit parce que la cellulle ne correspond pas à une case
    # d'étudiant, cette fonction va supprimer les lignes qui ne correspond pas
    # a des étudiants et nettoyer/organiser celles qui représentent des
    # étudiants.

    infos_reduites = False
    cell = garder_infos_utiles(cell)
    if len(cell) < 2:
        return []

    if len(cell) < 4:
        infos_reduites = True

    new_cell = []
    # Le numero étudiant
    new_cell.append(cell[0].split(" : ")[-1])

    # On ne prend pas en compte le nom de l'étudiant par soucis d'anonymité.

    # année d'arrivée à la fac
    new_cell.append("20" + new_cell[0][1:3])

    if not infos_reduites:
        # La date de naissance
        new_cell.append(cell[2].split(" ")[-2])

        # le code du lieu de naissance et la ville de naissance
        new_cell.append(cell[3].split(" ")[0])
        new_cell.append(" ".join(cell[3].split(" ")[1:]).strip())

        # True si l'etudiant est né en france métropolitaine
        new_cell.append(new_cell[3] == "02a" or new_cell[3] == "02b"
                        or int(new_cell[3]) <= 96)
        # True si l'etudiant est né à Toulouse
        new_cell.append(new_cell[3] == "031")
    else:
        new_cell += [None, None, None, None, None]
    return new_cell


def traiter_resultat(cell):
    # Transforme une cellule "resultat" pour qu'elle soit correctement formatée

    # Traite les résultats d'un élève sous la forme :
    # [note, points jury, code obtention (ADM, DEF, CMP, VAC, AJ, ADJ),
    # crédit du cours, mention, date  (année du début de l'année),
    # session]

    res = traiter_semestre(cell)
    return res


def traiter_semestre(case):
    # Transforme une cellule "semestre" pour qu'elle soit correctement formatée
    reussi = False
    if code_obtention(case) in code_reussite:
        reussi = True

    case = [
        note(case, True),
        points_jury(case),
        code_obtention(case),
        credit_cours(case),
        mention(case),
        date_session(case, reussi)[0],
        date_session(case, reussi)[1],
    ]
    return case


def traiter_matiere(case):
    # Transforme une cellule "matière" pour qu'elle soit correctement formatée
    reussi = False
    if code_obtention(case) in code_reussite:
        reussi = True
    case = [
        note(case, False),
        points_jury(case),
        code_obtention(case),
        credit_cours(case),
        mention(case),
        date_session(case, reussi)[0],
        date_session(case, reussi)[1],
    ]
    return case


def corriger_tableau(tableau):
    # Corige les informations dans le tableau. C'est a dire qu'on va formater
    # toutes les cases

    new_tableau = tableau.copy()
    # Certains dataframes ont des colonnes dupliquées, la ligne suivante les
    # supprime.
    new_tableau = new_tableau.loc[:, ~new_tableau.columns.duplicated()]
    col_droped = False
    for row_index, row in new_tableau.iterrows():
        row_droped = False
        for col_index, cell in row.items():
            new_cell = []

            if col_index == "identification":
                new_cell = traiter_identification(cell)
                if new_cell == []:
                    # cette ligne ne corespond pas à un étudiant donc on la
                    # supprime.
                    new_tableau.drop(row_index, axis=0, inplace=True)
                    row_droped = True

            elif col_index == "":
                # cette colonne ne corespond pas à un cours donc on la supprime.
                if not col_droped:
                    new_tableau.drop(col_index, axis=1, inplace=True)
                    col_droped = True

            elif col_index == "resultat":
                new_cell = traiter_resultat(cell)

            elif est_un_semestre(col_index):
                new_cell = traiter_semestre(cell)

            else:  # Cours normal
                new_cell = traiter_matiere(cell)
            # Si la cellulle n'a pas été supprimée, on la modifie
            if not row_droped and col_index != "":
                new_tableau.at[row_index, col_index] = new_cell
    return new_tableau


def second_traitement(liste_df, infos_pv_input):
    # réalise le second traitement des données
    global infos_pv
    infos_pv = infos_pv_input
    return [corriger_tableau(df) for df in liste_df]


################################################################################

####################################################
# Fonctions nécéssaires à la fusion des dataframes #
####################################################


def indexer_num_etudiant(tableau):
    # indexe le tableau par le num étudiant
    num_etudiants = [cell[0] for cell in tableau.identification]
    tableau.insert(loc=1, column="num_etudiant", value=num_etudiants)
    tableau.set_index("num_etudiant", inplace=True)
    return tableau


def fusionner_liste_df(liste_df):
    # fusionne les dataframes de chaque page en une seule

    liste_df_indexed = [indexer_num_etudiant(df) for df in liste_df]

    # On initialise le DataFrame
    fused_df = pd.DataFrame()

    for tableau in liste_df_indexed:
        for column in tableau.columns:
            if (column not in fused_df.columns
                ):  # Si la colonne n'existe pas, on la rajoute
                fused_df.insert(len(fused_df.columns), column, "")

        for num_etudiant, row in tableau.iterrows():
            if (num_etudiant not in fused_df.index
                ):  # Si l'etudiant n'a pas encore été rencontré, on le rajoute
                fused_df.loc[num_etudiant] = None
            for (
                    col_name,
                    value,
            ) in row.iteritems():  # On ajoute les infos du cours dans le df
                fused_df.at[num_etudiant, col_name] = value

    return fused_df
