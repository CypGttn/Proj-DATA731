import pandas as pd
import matplotlib.pyplot as plt

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
