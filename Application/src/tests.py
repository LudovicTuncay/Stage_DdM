from import_data import import_data
# import os
# from pdfminer.high_level import extract_text
import filetype

#file = "data/PVs Maths/M2/PV M2 ESR S1 2019-20.pdf"

#kind = filetype.guess(file)

# print(kind.extension)

import_data(
    "/Users/kaan/Cours/L3_SID_2020/S6/Stage DdM/Application/Fichiers_pdf_input/PV L1 Maths S1 2018-19.pdf")


# try:
#     text = extract_text(file, page_numbers=[2])
# except Exception:
#     text = extract_text(file, page_numbers=[1])

# useful_info = text[text.index("Session"):text.index("Date")]
# useful_info = useful_info.split("\n\n")

# print(useful_info)


# def get_niveau_et_formation(texte):
#     codes_annees = ["L1", "L2", "L3", "M1", "M2"]
#     codes_CUPGE = {"1ERE": "L1", "2EME": "L2", "3EME": "L3"}
#     texte = texte.split(" ")
#     print(texte)
#     for i, mot in enumerate(texte):
#         if mot in codes_CUPGE.keys():
#             niveau = codes_CUPGE[mot]
#             formation = " ".join(texte[i+2:]).strip()
#         elif mot in codes_annees:
#             niveau = mot
#             formation = " ".join(texte[i+1:]).strip()
#     return niveau, formation


# def recuperer_infos_pv(useful_info):
#     session_et_date = useful_info[0]
#     niveau_et_formation = useful_info[1]
#     num_session = session_et_date.split(" ")[1]
#     date = session_et_date.split(" ")[-1].split("/")[0]
#     niveau, formation = get_niveau_et_formation(niveau_et_formation)
#     return num_session, date, niveau, formation


# print(import_data(file)[1])
