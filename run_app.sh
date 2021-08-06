#!/bin/sh

# On traite les fichiers pdf
echo "Souhaitez traiter des procès verbeaux et les transformer en fichier csv ? (pensez a mettre des fichiers pdf dans Fichiers_pdf_input dans le dossier Application) [y,n]"
read reponse
while [[ $reponse != "y" && $reponse != "Y" && $reponse != "n" && $reponse != "N" ]]
do
    echo "Réponse inconnue !"
    echo "Souhaitez traiter des procès verbeaux et les transformer en fichier csv ? [y,n]"
    read reponse
done
if [[ $reponse == "y" || $reponse == "Y" ]]
then
    echo "Traitement des procès verbaux..."
    "./Application/venv_PDF/bin/python3" "./Application/src/main.py"
fi

# On transforme les fichiers csv en matrice de suivi 
echo "Souhaitez vous transformer les PVs au format csv en matrice de suivi ? (pensez a mettre des fichiers csv dans Fichiers_csv_output dans le dossier Application) [y,n]"
read reponse
while [[ $reponse != "y" && $reponse != "Y" && $reponse != "n" && $reponse != "N" ]]
do
    echo "Réponse inconnue !"
    echo "Souhaitez vous transformer les PVs au format csv en matrice de suivi ? [y,n]"
    read reponse
done
if [[ $reponse == "y" || $reponse == "Y" ]]
then
    echo "Transfomation des fichiers csv en matrice de suivi..."
    "./Application/venv_PDF/bin/python3" "./Application/src/suivi_etudiant.py"
fi

# On lance le dashboard
echo "Souhaitez vous lancer le dashboard afin d'observer et etudier les flux d'étudiants [y,n]"
read reponse
while [[ $reponse != "y" && $reponse != "Y" && $reponse != "n" && $reponse != "N" ]]
do
    echo "Réponse inconnue !"
    echo "Souhaitez vous lancer le dashboard afin d'observer et etudier les flux d'étudiants [y,n]"
    read reponse
done
if [[ $reponse == "y" || $reponse == "Y" ]]
then
    "./Dash/venv_Dash/bin/python3" "./Dash/dashboard.py"
fi