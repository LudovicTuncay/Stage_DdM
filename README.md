# README
Ces applications sont responsables du traitement des procès verbaux, de la transfomation en matrice de suivi de parcours et enfin d'un dashboard présentant les résultats
Elles ont été réalisées lors de mon stage au Département de Mathématiques de l'Université Paul Sabatier dans le cadre d'un stage pendant de ma L3 SID (2020/2021)


## Pré-requis :

il faut avoir téléchargé l'application et installer toutes les dépendances. Pour ce faire on va devoir suivre la démarche suivante :
* créer deux environements de travail :
    1. **venv_PDF**
        * **python -m venv "venv_PDF"** pour le créer
        * **source venv_PDF/bin/activate** pour l'activer
        * **pip install -r requirements_PDF.txt** pour installer les librairies nécéssaires
        * **deactivate** pour le désactiver
        * Il faut maintenant placer le dossier **venv_PDF** créé dans le dossier **Application**
    2. **venv_Dash**
        * **python -m venv "venv_Dash"** pour le créer
        * **source venv_Dash/bin/activate** pour l'activer
        * **pip install -r requirements_Dash.txt** pour installer les librairies nécéssaires
        * **deactivate** pour le désactiver
        * Il faut maintenant placer le dossier **venv_Dash** créé dans le dossier **Dash**

## Comment lancer l'application

1. Placer les PVs (au format pdf) à traiter dans le dossier **Application/Fichiers_pdf_input**
3. À partir d'un terminal, se placer dans le dossier Stage_DdM
4. Lancer le script **run_app.sh** à partir d'un terminal (commande : **./run_app.sh** il faudra peut etre lancer **chmod +x run_app.sh**)
5. Suivre les instructions affichées

### Notes
* Le fichier **Application/logfile.txt** détaille le déroulement de l'exécution de l'application
* Le dossier **Application/Fichier_pdf_erreur** receuille les PVs qui ont eu un problème lors de l'exécution (si c'est un scan par exemple)
* Le dossier **Application/Fichier_pdf_traites** receuille les PVs qui n'ont PAS eu de problème à l'exécution
* Le fichier généré **suivi_etudiant.csv** est le ficher prévu pour être utilisé dans le dashboard.


## Comment utiliser le dashboard

Le dashboard se présente sous cette forme

<img width="1440" alt="dashboard état initial" src="https://user-images.githubusercontent.com/54948149/128510115-ee78911b-07bd-4dc9-baf6-29c5325e4579.png">

* Commencez par selectionner un fichier à utiliser (idéalement le fichier **suivi_etudiant.csv** qui à été généré précédemment)
    * On peut glisser déposer le fichier dans la boite prévue à cet effet
    * On peut aussi cliquer dans la boite. Dans ce cas, une fenetre s'ouvrira pour selectionner un fichier
* Une fois le fichier importé, un appercu des données devrait s'afficher, par exemple : 
<img width="720" alt="dashboard après lecture d'un fichier" src="https://user-images.githubusercontent.com/54948149/128510673-4999c3f1-5d8b-41fa-8cc0-3ed485dbbb81.png">

* Vous pouvez maintenant faire des selections sur ce que vous souhaitez afficher:
    * On peut choisir la fenêtre de temps à afficher sur le graphe (Attention : cela ne change en rien les données et leur représentation sur le graphique de flux. Cela change juste la periode affichée. Par exemple un étudiant ayant obtenu un M2 en 2019/2020 sera affiché comme diplomé, même si on n'affiche qu'entre 2016/2017 et 2018/2019)
    * On peut choisir de fixer une ou plusieurs année pour les fillières que l'on va selectionner juste après (paramètre optionnel)
    * On fixe une ou plusieurs fillières, tous les étudiants qui ont été au moins une fois dans les combinaisons années/fillières seront affichés sur le graphe. Si aucune année n'est fixée, on affiche tous les étudiants qui ont été au moins une fois dans cette filière, peu importe l'année et le niveau (paramètre optionnel).
    * On peut fixer une année de présence pour les étudiants ci-dessus. Par exemple si on choisit 2017/2018, tous les étudiants affiché seront dans une des fillières ci-dessus en 2017/2018 (paramètre obligatoire).
    * Il y a plusieurs autres options :
        * On peut séparer les étudiants qui sont allés en deuxième session de ceux qui n'y sont pas allé (appliqué à chaque filière et chaque année étudiée)
        * On peut décider de n'afficher qu'un seul diplome (Correspond au diplome le plus "élevé" obtenu par un étudiant. Attention, un étudiant qui à un M2 ne sera pas marqué comme ayant une L2, même s'il l'a validé dans le passé (ce fait est changeable dans le code source, dans le fichier **callback_graphiques.py** au sein de la fonction update_selection_annees.)
        * On peut aussi décider d'afficher tous les diplomes. On affichera donc le meilleur diplome obtenu par chaque étudiant au sein de sa scolarité.
 * Une fois les options sélectionnées, vous pouvez cliquer sur le bouton "**Submit**"
    * Si on a pas fixé de fillières, un message d'erreur est affiché.
        * Attention : Si on modifie la fenetre de temps étudiée ou les niveaux choisis, vos choix de fillières seront réinitialisés. C'est pour qu'on ne puisse avoir que des choix existant dans le fichier soumis.

Si vous avez cliqué sur le bouton "**Submit**" avec tous les paramètres obligatoires remplis, un graphe devrait s'afficher rapidement. Si ce n'est pas le cas, essayez de cliquer de nouveau sur le bouton "**Submit**".

### Le graphe
<img width="1440" alt="Capture d’écran 2021-08-06 à 14 54 54" src="https://user-images.githubusercontent.com/54948149/128513424-3589324f-0e2f-4bdb-9219-a3fb889e1d0d.png">

Une fois le graphe affiché, il est accompagné d'une légende, et d'un menu pour choisir quel type de selection on souhaite utiliser :
    1. Par formation : si on clique ou qu'on survole une formation, c'est toute la formation qui sera selectionnée.
    2. Par couleur (diplome) : uneiquement les étudiants d'une même formation et ayant la même couleur (ayant obtenu le même diplome) seront selectionnés.
    3. Par année : tous les étudiants seront selectionnés
Dans tous les cas, lorsque l'on survole le graphe avec la souris, des information seront affichées. Et si on clique sur une catégorie, de nouvelles informations seront affichées. Entre autres, le nombre d'étudiants selection, quelle proportion à obtenu le diplome, etc ...

Un nouveau graphe est aussi affiché. Il y a deux possibilités :
1. lorsque l'on a selectionné des étudiants par formation ou par année. Un graphe représentant la moyenne des étudiants durant toute leur scolarité en fonction du nombre d'années passées à l'université est affiché. Les points sont colorés en fonction de leur diplome. Il est aussi accompagné d'un histograme par axe pour mieux comprendre la répartition des données.
    * Note : on peut cliquer sur les diplomes dans la légende pour désactiver ou activer certains diplomes.
2. Lorsque l'on a selectionné les étudiants par couleur (diplome) il y a encore une fois deux possibilités
    1. Si on a selectionné des diplomés, on affiche la répartition du nombre d'années passée à l'université avant d'avoir obtenu le diplome.
        * En bleu sont les étudiants qui ont mis moins de temps que le temps normal pour obtenir ce diplome. C'est surement du au fait qu'ils arrivent d'un autre établissement
        * En vert, ce sont les étudiants qui on mit autant de temps que "prévu" pour obtenir ce diplome. C'est surement car ils n'ont jamais redoublé. Attention, ca peut aussi etre le cas si une personne est arrivée en cours de route depuis un autre établissement et puis a redoublé.
        * En jaune ce sont les étudiant qui n'ont eu qu'une année de retard. Cela peut etre du par un redoublement ou par une réorientation
        * En rouge, ce sont les étudiant qui ont eu deux ans ou plus de retard dans leur parcours.
    2. Si on a selectionné des non-diplomés, on affiche la répartition du nombre d'années passées depuis leur inscription à l'université.

Il n'est malheureusement pas possible d'afficher les étudiants en question sur le graphe de flux ou bien d'afficher leur numéro étudiant. Il ne devrait pas être trop difficile d'adapter le code pour que cela soit possible, mais nous avons pas eu le temps de rendre cela possible.

Il est bon de noter qu'une capture d'écran des graphes est possible. Pour ce faire, il suffit de cliquer sur le petit appareil photo qui s'affiche dans la barre de menu lorsque l'on survole le graphe.
