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

# Ajouter des labels et une légende
plt.xlabel('Date')
plt.ylabel('Température (°C)')
plt.title('Températures des villes en fonction du temps')
plt.legend()

# Afficher le graphique
plt.xticks(rotation=45)
plt.tight_layout()  # Pour éviter que les labels ne se chevauchent
plt.show()

def get_interval(season):
    #date1 = datetime(2000, 5, 15)  # 15 mai (année arbitraire)
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

seasons = ["spring", "summer", "autumn","winter"]
am_per_season = []
######### Entropie relative local pour la meme saison sur deux annees
for season in seasons: # pour les 4 saisons 
    interval = get_interval(season)
    start_date = interval[0].replace(year=1940)

    if season == "winter":
        end_date = interval[1].replace(year=1941)
    else:
        end_date = interval[1].replace(year=1940)
    

    am = [] 
    #m_values = range(200, t - 200)  # Créer une liste de m pour l'axe des abscisses
    for i in range(80):  
        # Filtrer les lignes entre start_date et end_date
        
        filtered_df1 = df[(df['LOCAL_DATE'] >= start_date) & (df['LOCAL_DATE'] <= end_date)]
        filtered_df2 = df[(df['LOCAL_DATE'] >= start_date.replace(year=start_date.year+1)) & (df['LOCAL_DATE'] <= end_date.replace(year=end_date.year+1))]

        # Créer les sous-ensembles u et v 
        u = filtered_df1['MEAN_TEMPERATURE_OTTAWA']      # saison annee 1
        v = filtered_df2['MEAN_TEMPERATURE_OTTAWA']      # saison annee 2

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


    # Ajouter am pour cette station dans la liste principale
    am_per_season.append(am)

# Tracer tous les am sur un même graphique avec m en abscisse
plt.figure(figsize=(10, 6))

for index, am in enumerate(am_per_season):
    plt.plot(am, label=seasons[index])  # Utiliser les saisons comme légende

# Ajouter un titre et des labels
plt.title('Courbe des valeurs des divergences pour toutes les saisons')
plt.xlabel('Années à partir de 1940')
plt.ylabel('Valeurs de divergence')
plt.grid(True)
plt.legend()  # Ajouter une légende pour identifier les saisons
plt.show()