import pandas as pd
import numpy as np

def quick_dataset_summary(df, top_n=5, verbose=True):
    """
    Présentation rapide et complète d'un DataFrame Pandas.
    
    Args:
        df (pd.DataFrame): le dataset à analyser
        top_n (int): nombre de valeurs uniques les plus fréquentes à afficher pour les colonnes qualitatives
        verbose (bool): afficher le résumé
    
    Returns:
        None
    """
    
    if not verbose:
        return
    
    print("=== Dimensions ===")
    print(f"Lignes : {df.shape[0]}, Colonnes : {df.shape[1]}\n")
    
    print("=== Aperçu des premières lignes ===")
    print(df.head(top_n), "\n")
    
    print("=== Types de colonnes ===")
    print(df.dtypes, "\n")
    
    print("=== Valeurs manquantes ===")
    missing = df.isna().sum()
    missing_percent = (missing / len(df) * 100).round(2)
    missing_df = pd.DataFrame({'missing_count': missing, 'missing_percent': missing_percent})
    print(missing_df[missing_df['missing_count'] > 0].sort_values('missing_count', ascending=False), "\n")
    
    print("=== Statistiques descriptives (numériques) ===")
    print(df.describe().T, "\n")
    
    print("=== Colonnes qualitatives ===")
    cat_cols = df.select_dtypes(include=['object', 'category']).columns
    if len(cat_cols) == 0:
        print("Aucune colonne qualitative détectée.\n")
    else:
        for col in cat_cols:
            print(f"\n-- {col} --")
            print(df[col].value_counts(dropna=False).head(top_n))
    
    print("\n=== Corrélations (numériques) ===")
    num_cols = df.select_dtypes(include=np.number).columns
    if len(num_cols) > 1:
        print(df[num_cols].corr().round(2))
    else:
        print("Pas assez de colonnes numériques pour calculer une corrélation.")