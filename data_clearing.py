import pandas as pd

# Chemin vers le fichier CSV
chemin_fichier = 'Canadian_climate_history.csv'

# Chargement du CSV dans un DataFrame
df = pd.read_csv(chemin_fichier)

# Afficher les premières lignes du DataFrame
print(df.head())

filtre_remove = ["MEAN_TEMPERATURE_SASKATOON","TOTAL_PRECIPITATION_SASKATOON","MEAN_TEMPERATURE_EDMONTON","TOTAL_PRECIPITATION_EDMONTON","MEAN_TEMPERATURE_HALIFAX","TOTAL_PRECIPITATION_HALIFAX","MEAN_TEMPERATURE_MONTREAL","TOTAL_PRECIPITATION_MONTREAL","MEAN_TEMPERATURE_QUEBEC","TOTAL_PRECIPITATION_QUEBEC","MEAN_TEMPERATURE_STJOHNS","TOTAL_PRECIPITATION_STJOHNS","MEAN_TEMPERATURE_WHITEHORSE","TOTAL_PRECIPITATION_WHITEHORSE"]

updated_df = df.drop(columns=filtre_remove)

# Enregistrer le DataFrame en CSV
updated_df.to_csv('canadian_climate_change_history_updated.csv', index=False)