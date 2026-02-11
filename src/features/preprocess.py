# 1 - Importer le fichier 
# 2 - Supprimer les colonnes inutiles 
# 3 - Vérifier format colonnes
# 4 - Explode : genres, pays d'origine
# 5 - Standardiser données (StandardScaler pour le numérique et get_dummies qualitatives faibles cardinalité et ? forte cardilanités)


import pandas as pd
from src.config import *
df = pd.read_csv(OUTPUT_DIR / "10_final_imdb_tmdb.csv")


