---
🎬 Movie Recommender App — IMDb & TMDB Data Pipeline
---
==> Demo live :
https://https://cinedata.streamlit.app/

---
🧠 Présentation du projet
---
Ce projet consiste à construire un système complet de recommandation de films, depuis le traitement de données brutes jusqu’à leur exploitation dans une application interactive.

Il s’agit d’un projet end-to-end Data comprenant :

ingestion et nettoyage de datasets réels (IMDb & TMDB)

création d’un dataset enrichi

feature engineering pour Machine Learning

développement d’un moteur de recommandation basé sur la similarité

mise en production dans une application Streamlit

L’objectif est de reproduire, à une échelle réaliste, la chaîne complète d’un produit data.

---
🚀 Description de l’application
---

L’application permet de :

explorer un catalogue de films

consulter des fiches détaillées

obtenir des recommandations personnalisées

naviguer entre les films similaires

---
🎯 Objectifs du projet
---
Ce projet vise à démontrer :

la capacité à construire un pipeline data complet

la maîtrise du feature engineering pour le NLP

l’implémentation d’un moteur de recommandation basé contenu

la mise en production d’un modèle ML dans une interface utilisateur

---
📊 Fonctionnalités principales : Pipeline Data Engineering
--
nettoyage des données IMDb

filtrage des films pertinents

enrichissement avec TMDB

extraction des informations clés (casting, réalisateurs…)

fusion multi-sources

production d’un dataset final prêt pour le ML

---
🤖 Moteur de recommandation
---
Le système de recommandation repose sur :

un modèle Nearest Neighbors

une similarité cosinus

des features hybrides combinant :

texte (TF-IDF)

catégories (MultiLabelBinarizer)

variables numériques normalisées

Le moteur permet d’identifier des films similaires selon :

genre

casting

réalisateurs

popularité

caractéristiques textuelles

---
🖥 Application Streamlit
---
L’interface propose :

navigation dans un catalogue complet

fiches films détaillées

recommandations dynamiques

design personnalisé avec CSS

---
📁 Structure du projet
---
```text
imdb-project-streamlit/
│
├── app.py                     # Entrée principale Streamlit
│
├── assets/
│   └── style.css              # Styles personnalisés UI
│
├── pages/                     # Pages de l'application
│   ├── Catalogue.py
│   ├── Film_details.py
│   ├── Reco_ML.py
│   └── Espace_client.py
│
├── src/
│   ├── config.py
│   ├── pipeline.py            # Orchestration du pipeline
│   ├── utils.py
│   ├── ui.py
│   │
│   ├── reco/                  # Moteur ML
│   │   ├── engine.py
│   │   └── preprocess.py
│   │
│   ├── s01 → s10              # Étapes pipeline data
│
├── docs/
├── requirements.txt
└── README.md
```
---
⚙️ Pipeline de traitement des données
---
Le pipeline comporte plusieurs étapes :

Chargement des données IMDb

Filtrage des titres pertinents

Nettoyage des ratings

Sélection des films principaux

Extraction des réalisateurs

Enrichissement du casting

Consolidation des informations

Création du dataset IMDb final

Nettoyage des données TMDB

Fusion des deux sources

Chaque étape produit des artefacts intermédiaires permettant la reproductibilité du processus.

---
🤖 Détails techniques du moteur de recommandation
---
Features utilisées

genres

pays

popularité

année de sortie

réalisateurs

texte (casting + description)

Préparation des données

TF-IDF pour les données textuelles

MultiLabelBinarizer pour les catégories

StandardScaler pour les variables numériques

Algorithme utilisé
NearestNeighbors(metric="cosine")

Ce choix permet :

de gérer efficacement les données sparse

d’obtenir des recommandations pertinentes sur des données textuelles

d’assurer des performances rapides en production

🛠 Installation locale
git clone https://github.com/anthjatowrth/imdb-project-streamlit.git
cd imdb-project-streamlit

python -m venv .venv
source .venv/Scripts/activate

pip install -r requirements.txt

---
▶️ Lancer l’application
---
streamlit run app.py

---
📦 Données
---
Les datasets ne sont pas inclus pour des raisons de taille.

Sources utilisées :

IMDb datasets (officiels)

export TMDB

🎓 Contexte du projet

Projet réalisé dans le cadre d’une formation Data Analyst à la Wild Code School.

---
✨ Points forts du projet
---
pipeline data complet et reproductible

fusion multi-sources réalistes

feature engineering avancé

moteur de recommandation performant

application interactive déployée

architecture modulaire professionnelle


👨‍💻 Auteur

Anthony — Data Analyst 
