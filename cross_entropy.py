import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import entropy
from datetime import datetime

# Charger les données
df = pd.read_csv('canadian_climate_change_history_updated.csv')
df['LOCAL_DATE'] = pd.to_datetime(df['LOCAL_DATE'], format='%d-%b-%Y %H:%M:%S')

# Fonction pour obtenir l'intervalle de dates d'une saison
def get_season_dates(season, year=1940):
    if season == "winter":
        start_date = datetime(year, 12, 21)
        end_date = datetime(year + 1, 3, 19)
    elif season == "spring":
        start_date = datetime(year, 3, 20)
        end_date = datetime(year, 6, 20)
    elif season == "summer":
        start_date = datetime(year, 6, 21)
        end_date = datetime(year, 9, 21)
    elif season == "autumn":
        start_date = datetime(year, 9, 22)
        end_date = datetime(year, 12, 20)
    
    return start_date, end_date

# Sélectionner une ville
city = 'CALGARY'

# Calculer l'entropie croisée pour chaque année de 1941 à 2020
years = list(range(1941, 2021))
cross_entropy_values = []

for year in years:
    # Filtrer les températures pour la saison hiver de l'année donnée
    start_date, end_date = get_season_dates("winter", year)
    season_data = df[(df['LOCAL_DATE'] >= start_date) & (df['LOCAL_DATE'] <= end_date)]
    
    # Extraire les températures de la ville pour cette saison
    season_temp = season_data['MEAN_TEMPERATURE_' + city].dropna()
    
    # Si on est à la première année (1941), on prend l'année précédente (1940) pour calculer l'entropie croisée
    if year == 1941:
        prev_start_date, prev_end_date = get_season_dates("winter", 1940)
        prev_season_data = df[(df['LOCAL_DATE'] >= prev_start_date) & (df['LOCAL_DATE'] <= prev_end_date)]
        prev_season_temp = prev_season_data['MEAN_TEMPERATURE_' + city].dropna()
        
        # Créer des histogrammes pour l'année précédente et l'année actuelle
        hist_prev, bin_edges = np.histogram(prev_season_temp, bins=30, density=True)
        hist_current, _ = np.histogram(season_temp, bins=30, density=True)
        
        # Normaliser les histogrammes
        hist_prev = hist_prev / np.sum(hist_prev)
        hist_current = hist_current / np.sum(hist_current)
        
        # Calculer l'entropie croisée pour cette paire d'années
        cross_entropy = -np.sum(hist_prev * np.log(hist_current + 1e-10))  # Ajout de 1e-10 pour éviter log(0)
    
    else:
        # Pour les années suivantes, utiliser l'année précédente pour comparer
        prev_start_date, prev_end_date = get_season_dates("winter", year - 1)
        prev_season_data = df[(df['LOCAL_DATE'] >= prev_start_date) & (df['LOCAL_DATE'] <= prev_end_date)]
        prev_season_temp = prev_season_data['MEAN_TEMPERATURE_' + city].dropna()
        
        # Créer des histogrammes pour l'année précédente et l'année actuelle
        hist_prev, bin_edges = np.histogram(prev_season_temp, bins=30, density=True)
        hist_current, _ = np.histogram(season_temp, bins=30, density=True)
        
        # Normaliser les histogrammes
        hist_prev = hist_prev / np.sum(hist_prev)
        hist_current = hist_current / np.sum(hist_current)
        
        # Calculer l'entropie croisée pour cette paire d'années
        cross_entropy = -np.sum(hist_prev * np.log(hist_current + 1e-10))  # Ajout de 1e-10 pour éviter log(0)

    cross_entropy_values.append(cross_entropy)

# Afficher les résultats sous forme de graphique
plt.figure(figsize=(10, 6))
plt.plot(years[1:], cross_entropy_values[1:], marker='o', color='b', label='Entropie croisée entre années')
plt.title(f"Entropie croisée des températures hivernales de 1941 à 2020 pour {city}")
plt.xlabel("Année")
plt.ylabel("Entropie croisée")
plt.grid(True)
plt.tight_layout()
plt.show()
