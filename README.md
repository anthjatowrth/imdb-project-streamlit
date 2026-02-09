Ce dépôt contient un pipeline de préparation des données IMDb et TMDB, structuré en étapes clairement numérotées.
Les données ne sont pas versionnées dans le dépôt pour éviter les limitations de taille GitHub et faciliter la reconstruction locale du jeu de données.

```text
📁 Structure du projet
imdb-project-streamlit/
│
├── src/                     # Scripts de pipeline
│   ├── config.py
│   ├── pipeline.py
│   ├── utils.py
│   ├── s01_basics.py
│   ├── s02_akas_fr.py
│   ├── s03_ratings_filtered.py
│   ├── s04_core_movies.py
│   ├── s05_crew_directors.py
│   ├── s06_principals_cast_producers.py
│   ├── s07_names.py
│   ├── s08_imdb_final.py
│   ├── s09_tmdb_clean.py
│   └── s10_merge_imdb_tmdb.py
│
├── .gitignore
└── README.md
```

---
🧰 Objectif
---
Ce projet permet de :

Télécharger les jeux de données bruts (IMDb + TMDB)

Exécuter une série d’étapes de préparation (nettoyage, filtrage, fusion)

Générer des jeux de données finaux prêts à être utilisés dans une application ou une analyse

Chaque script sXX_*.py représente une étape spécifique du pipeline.

Fournir une data app Streamlit qui permet à un utilisateur d'obtenir des recommandations de films en fonction de ces choix, basée sur le dataset final filtré. 

---
📌 Contexte du projet
---

Ce projet a été réalisé dans le cadre d’une formation en data analyse, en collaboration avec Stéphanie Berard, Pierre Guerlais et Waguih Yahya

Le dépôt est volontairement très détaillé et structuré, avec de nombreuses étapes intermédiaires et de la documentation.

L’objectif n’est pas uniquement de fournir une application fonctionnelle, mais également de présenter de manière explicite l’ensemble du pipeline de traitement des données : extraction, nettoyage, transformation, enrichissement, fusion des sources et visualisation.

Ce niveau de détail vise à rendre le projet pédagogique, transparent et facilement compréhensible, aussi bien pour l’apprentissage que pour une relecture technique.

---
📥 Installation locale
---
Clone le dépôt :

git clone https://github.com/anthjatowrth/imdb-project-streamlit.git
cd imdb-project-streamlit

---
⚙️ Environnement Python
---
Crée un environnement virtuel recommandé :

Windows

python -m venv .venv

.venv\Scripts\activate

macOS / Linux

python -m venv .venv

source .venv/bin/activate

---
Installer les dépendances
---
py -m pip install --upgrade pip

py -m pip install -r requirements.txt

---
📂 Création des dossiers de données
---
Avant d’exécuter les scripts, crée les dossiers nécessaires :

mkdir -p data/raw data/interim data/output

---
📦 Récupération des données brutes
---
Les jeux de données ne sont pas inclus dans le dépôt. Tu peux les télécharger depuis les sources officielles :

IMDb : https://datasets.imdbws.com/

TMDB : fichier CSV local ou API

Télécharge les fichiers dans :

data/raw/


Par exemple :

data/raw/title.basics.tsv.gz

data/raw/title.ratings.tsv.gz

data/raw/name.basics.tsv.gz

data/raw/tmdb_full.csv

---
🔄 Exécution du pipeline
---
Le pipeline est organisé en 10 étapes :

python src/s01_basics.py

python src/s02_akas_fr.py

python src/s03_ratings_filtered.py

...

python src/s10_merge_imdb_tmdb.py

Pour les exécuter dans l'ordre, tu dois tout simplement exécuter le fichier pipeline.py

Chaque script produit des fichiers intermédiaires dans :

data/interim/


Puis les résultats finaux dans :

data/output/

---
📌 À propos des scripts
---
Voici brièvement ce que font les principaux scripts :

s01_basics.py → lecture des données principales (films, séries)

s02_akas_fr.py → filtrage des titres français

s03_ratings_filtered.py → filtrage des notes

s04_core_movies.py → extraction des films principaux

s05_crew_directors.py → récupération des réalisateurs

s06_principals_cast_producers.py → casting, producteurs

s07_names.py → données personnes (acteurs, crew)

s08_imdb_final.py → agrégation IMDb finale

s09_tmdb_clean.py → nettoyage TMDB

s10_merge_imdb_tmdb.py → fusion IMDb + TMDB

(les noms sont explicites et suivent l’ordre du pipeline)


---
Présentation datasets et nettoyage 
---
<img width="906" height="1276" alt="image" src="https://github.com/user-attachments/assets/e35379ce-28c9-4009-9a2f-9dad4c183daf" />


---
🛠 quick_summary_function.py
---
Le fichier quick_summary_function.py contient une fonction utilitaire personnalisée, développée spécifiquement pour ce projet.

Son objectif est de fournir un aperçu rapide et synthétique d’un jeu de données, notamment :

La structure générale et les dimensions

Les types de colonnes

Les valeurs manquantes

Les statistiques descriptives principales

Des exemples de valeurs

Cette fonction permet d’accélérer la phase d’exploration des données (EDA) et d’identifier rapidement d’éventuels problèmes de qualité avant les étapes de traitement plus avancées.

---
🧪 Validation et tests
---
Tu peux vérifier la bonne création des fichiers intermédiaires et finaux avec :

ls data/interim
ls data/output

Et ouvrir les fichiers générés avec pandas par exemple.

---
# Dossier data
---
Ce dossier contient les données du pipeline. Il n’est pas versionné.

Structure :

- raw/     : sources brutes (IMDb, TMDB)
- interim/ : données intermédiaires nettoyées
- output/  : jeux de données finaux


