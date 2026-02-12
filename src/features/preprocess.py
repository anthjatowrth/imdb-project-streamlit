# 1 - Importer le fichier 
# 2 - Supprimer les colonnes inutiles 
# 3 - Vérifier format colonnes
# 4 - Explode : genres, pays d'origine
# 5 - Standardiser données (StandardScaler pour le numérique et get_dummies qualitatives faibles cardinalité et ? forte cardilanités)


import pandas as pd
from src.config import *
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler


df = pd.read_csv(OUTPUT_DIR / "10_final_imdb_tmdb.csv")

X = [["Année_de_sortie", "Durée", "Genre", "Note_moyenne", "Nombre_votes", " Réalisateurs", "Casting", "Pays_origine", "Boite_de_production"]]

X_query = df[(df['Titre'] == "Titanic") & (df['Année_de_sortie'] == 1997)]

vectorizer = TfidfVectorizer(tokenizer=lambda x: x.split())