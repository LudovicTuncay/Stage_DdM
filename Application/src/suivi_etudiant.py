import pandas as pd
import os
import sys
import numpy as np
from tqdm import tqdm
from collections import Counter
import numpy as np

csv_files_path = "Fichiers_csv_output"
codes_valides = ["adm", "adj"]
valeur_annee = {
    None: 0,
    "Hors": 0,
    "L1": 1,
    "3LA": 1,
    "L2": 2,
    "L3": 3,
    "M1": 4,
    "M2": 5,
}


def get_infos(csv_file_name):
    name = csv_file_name.split(".")[0]

    dates = name.split(" ")[-1]
    year = int(dates.split("-")[0])
    dates = f"{year}/{year+1}"

    session = name.split(" ")[-2]

    niveau = name.split(" ")[1]

    domaine = "_".join(name.split(" ")[2:-2])

    return dates, niveau, domaine, session


def ajouter_au_suivi(csv_file_name, dataframe_suivi_etudiant):
    suivi_df = dataframe_suivi_etudiant.copy()

    dates, niveau, domaine, session = get_infos(csv_file_name)

    if dates not in suivi_df.columns:

        suivi_df[dates] = "Hors"

    df = pd.read_csv(
        os.path.join(csv_files_path, csv_file_name),
        header="infer",
        index_col="num_etudiant",
        sep=";",
    )

    for etudiant, res in zip(df.identification, df.resultat):
        identification = eval(etudiant)
        note, pt_jury, code = eval(res)[:3]
        inclure_note = True

        if pt_jury is None or np.isnan(pt_jury):
            pt_jury = 0
        if note is None or np.isnan(note):
            note = 0  # pour eviter une erreur après
            inclure_note = False
        moyenne_annee = note + pt_jury

        num_etudiant = identification[0]

        if num_etudiant not in suivi_df.index:
            new_etudiant = [
                "Hors"
                if col
                not in [
                    "last_annee_validee",
                    "last_diplome_valide",
                    "moyenne",
                    "nb_presence_pv",
                ]
                else None
                for col in suivi_df.columns
            ]

            suivi_df.loc[num_etudiant] = new_etudiant

        if inclure_note:
            previous_moyenne = suivi_df.loc[num_etudiant, "moyenne"]
            if previous_moyenne is None or np.isnan(previous_moyenne):
                suivi_df.loc[num_etudiant, "moyenne"] = moyenne_annee
                suivi_df.loc[num_etudiant, "nb_presence_pv"] = 1
            else:
                suivi_df.loc[num_etudiant, "moyenne"] += moyenne_annee
                suivi_df.loc[num_etudiant, "nb_presence_pv"] += 1

        # On vérifie que la session qu'on inscrit est bien supérieure a celle
        # qui existe déja (si il y en a une renseignée dans la cellule)
        # Si il n'y a rien dans la cellule, on la remplit normalement.
        split_content = suivi_df.loc[num_etudiant, dates].split(" - ")
        if len(split_content) <= 1 or split_content[-1] < session:
            suivi_df.loc[num_etudiant, dates] = f"{niveau} {domaine} - {session}"

        niveau_valide = suivi_df.loc[num_etudiant, "last_diplome_valide"]
        if code in codes_valides and valeur_annee[niveau] > valeur_annee[niveau_valide]:
            suivi_df.loc[num_etudiant, "last_diplome_valide"] = niveau
            suivi_df.loc[num_etudiant, "last_annee_validee"] = dates
    return suivi_df


def creer_suivi_etudiant():
    suivi_df = pd.DataFrame(
        columns=[
            "num_etudiant",
            "last_annee_validee",
            "last_diplome_valide",
            "moyenne",
            "nb_presence_pv",
        ]
    )
    suivi_df.set_index("num_etudiant", inplace=True)

    os.chdir(os.path.dirname(sys.path[0]))

    csv_files = [
        file for file in os.listdir(path=csv_files_path) if file.split(".")[-1] == "csv"
    ]

    for csv_file in tqdm(csv_files, desc="Fichiers traités"):
        suivi_df = ajouter_au_suivi(csv_file, suivi_df)

    suivi_df["moyenne"] = np.where(
        suivi_df["moyenne"] is None,
        np.nan,
        suivi_df["moyenne"] / suivi_df["nb_presence_pv"],
    )

    suivi_df["moyenne"] = [round(moyenne, 2) for moyenne in suivi_df["moyenne"]]

    suivi_df.drop(columns="nb_presence_pv", inplace=True)

    suivi_df = suivi_df.reindex(sorted(suivi_df.columns), axis=1)
    return suivi_df


def garder_niveau_et_formation(cell):
    return cell.split(" - ")[0]


# inutile mainentant qu'on sait que ce n'est pas utilisable
# def creer_matrice_evolution(
#     dataframe_suivi_etudiant,
#     annee_origine,
#     niveau_origine,
#     domaine_origine,
#     annees_precedentes=True,
# ):
#     suivi_df = dataframe_suivi_etudiant.copy()

#     suivi_df = suivi_df[
#         suivi_df[annee_origine].str.contains(f"{niveau_origine} {domaine_origine}")
#     ]

#     suivi_df.drop(["last_annee_validee", "last_diplome_valide"], axis=1, inplace=True)

#     suivi_df = suivi_df.applymap(garder_niveau_et_formation)

#     liste = [
#         dataframe_suivi_etudiant.at[num_etudiant, "last_annee_validee"] == "M2"
#         and suivi_df.at[num_etudiant, "2019/2020"] == "M2 SID"
#         for num_etudiant in suivi_df.index
#     ]

#     suivi_df["diplome_sid"] = liste

#     # suivi_copy = suivi_df.drop("2021")
#     suivi_df.to_csv("matrice_suivi_pour_graphe.csv", sep=";", na_rep="None")

#     #print(suivi_df)

#     matrice = pd.DataFrame(columns=["Annee_et_filliere"] + suivi_df.columns.tolist())
#     matrice.set_index("Annee_et_filliere", inplace=True)

#     for annee in suivi_df.columns.tolist():
#         fillieres_dict = {}
#         column = suivi_df.loc[:, annee].tolist()
#         fillieres_dict = Counter(column)
#         for filliere in fillieres_dict.keys():
#             if filliere not in matrice.index:
#                 new_filliere = [0 for _ in matrice.columns]
#                 matrice.loc[filliere] = new_filliere

#             matrice.loc[filliere, annee] = fillieres_dict[filliere]
#     return matrice


if __name__ == "__main__":

    suivi_df = creer_suivi_etudiant()
    suivi_df.to_csv("suivi_etudiant.csv", sep=";", na_rep="None")

    # inutile mainentant qu'on sait que ce n'est pas utilisable
    # matrice = creer_matrice_evolution(suivi_df, "2016/2017", "L2", "Maths")
    # matrice.to_csv("matrice_suivi.csv", sep=";", na_rep="None")
