import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Charger le DataFrame depuis un fichier CSV (à ajuster selon votre chemin de fichier)
df = pd.read_csv('canadian_climate_change_history_updated.csv')

# Convertir la colonne 'LOCAL_DATE' en datetime
df['LOCAL_DATE'] = pd.to_datetime(df['LOCAL_DATE'], format='%d-%b-%Y %H:%M:%S')

# Filtrer les colonnes contenant les températures (en supposant qu'elles commencent par 'MEAN_TEMPERATURE')
temperature_columns = [col for col in df.columns if 'MEAN_TEMPERATURE' in col]

# Tracer les températures de toutes les villes
plt.figure(figsize=(10, 6))

for city in temperature_columns:
    plt.plot(df['LOCAL_DATE'], df[city], label=city)  # Tracer la température pour chaque ville

# Ajouter des labels
plt.xlabel('Date')
plt.ylabel('Température (°C)')
plt.title('Températures des villes en fonction du temps')

# Option pour afficher ou masquer la légende
show_legend = True  # Modifiez ici à False pour masquer la légende

if show_legend:
    plt.legend()

# Afficher le graphique
plt.xticks(rotation=45)
plt.tight_layout()  # Pour éviter que les labels ne se chevauchent
plt.show()

def get_interval(season):
    res = ""
    if season == "spring":
        res = [datetime(1940, 3, 20),datetime(1940, 6, 20)]
    if season == "summer":
        res = [datetime(1940, 6, 21),datetime(1940, 9, 21)]
    if season == "autumn":
        res = [datetime(1940, 9, 22),datetime(1940, 12, 20)]
    if season == "winter":
        res = [datetime(1940, 12, 21),datetime(1940, 3, 19)]
    return res

city_list = ["CALGARY","MONCTON","OTTAWA","TORONTO","VANCOUVER","WINNIPEG"]
seasons = ["spring", "summer", "autumn", "winter"]
am_per_city = []

# Calcul des divergences par saison pour chaque ville
for city in city_list:
    am_per_season = []  # Pour stocker les divergences par saison pour chaque ville
    
    for season in seasons:  # pour les 4 saisons 
        interval = get_interval(season)
        start_date = interval[0].replace(year=1940)

        if season == "winter":
            end_date = interval[1].replace(year=1941)
        else:
            end_date = interval[1].replace(year=1940)

        am = [] 
        for i in range(80):  
            # Filtrer les lignes entre start_date et end_date
            filtered_df1 = df[(df['LOCAL_DATE'] >= start_date) & (df['LOCAL_DATE'] <= end_date)]
            filtered_df2 = df[(df['LOCAL_DATE'] >= start_date.replace(year=start_date.year+1)) & (df['LOCAL_DATE'] <= end_date.replace(year=end_date.year+1))]

            # Créer les sous-ensembles u et v 
            u = filtered_df1['MEAN_TEMPERATURE_' + city]  # saison année 1
            v = filtered_df2['MEAN_TEMPERATURE_' + city]  # saison année 2

            # Calculer la moyenne et la variance des sous-ensembles
            m1 = np.mean(u)
            v1 = np.var(u, ddof=1)
            m2 = np.mean(v)
            v2 = np.var(v, ddof=1)

            # Calculer divergence
            d = (1/2) * ((m1 - m2) ** 2 / (v1 + v2)) + (1/2) * ((v2 / v1) + (v1 / v2)) - 1
            am.append(d)
        
            start_date = start_date.replace(year=start_date.year+1)
            end_date = end_date.replace(year=end_date.year+1)

        # Ajouter les divergences de cette saison pour cette ville
        am_per_season.append(am)

    # Ajouter les divergences de toutes les saisons pour cette ville
    am_per_city.append(am_per_season)

# Tracer les divergences de chaque ville pour toutes les saisons
plt.figure(figsize=(10, 6))

# Tracer les courbes pour chaque ville
for city_index, city_am in enumerate(am_per_city):
    for season_index, am in enumerate(city_am):
        plt.plot(am, label=f'{city_list[city_index]} - {seasons[season_index]}')

# Ajouter un titre et des labels
plt.title('Divergence pour chaque ville et saison')
plt.xlabel('Années à partir de 1940')
plt.ylabel('Valeurs de divergence')
plt.grid(True)

# Option pour afficher ou masquer la légende
if show_legend:
    plt.legend(loc='best')  # Ajouter une légende pour identifier les villes et saisons

plt.tight_layout()
plt.show()
