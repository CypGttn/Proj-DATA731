import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from dash import Dash, dcc, html, Input, Output

# Charger les données
df = pd.read_csv('canadian_climate_change_history_updated.csv')
df['LOCAL_DATE'] = pd.to_datetime(df['LOCAL_DATE'], format='%d-%b-%Y %H:%M:%S')

# Définir les intervalles saisonniers
def get_interval(season):
    if season == "spring":
        return [datetime(1940, 3, 20), datetime(1940, 6, 20)]
    if season == "summer":
        return [datetime(1940, 6, 21), datetime(1940, 9, 21)]
    if season == "autumn":
        return [datetime(1940, 9, 22), datetime(1940, 12, 20)]
    if season == "winter":
        return [datetime(1940, 12, 21), datetime(1941, 3, 19)]
    return []

city_list = ["CALGARY", "MONCTON", "OTTAWA", "TORONTO", "VANCOUVER", "WINNIPEG"]
seasons = ["spring", "summer", "autumn", "winter"]

# Calculer les corrélations pour chaque ville et chaque saison
correlations_per_city = {}
for city in city_list:
    city_corr = []
    for season in seasons:
        interval = get_interval(season)
        start_date = interval[0].replace(year=1940)
        end_date = interval[1].replace(year=1940 if season != "winter" else 1941)
        
        corrs = []
        for i in range(80):  # Comparer sur 80 cycles (années)
            filtered_df1 = df[(df['LOCAL_DATE'] >= start_date) & (df['LOCAL_DATE'] <= end_date)]
            filtered_df2 = df[(df['LOCAL_DATE'] >= start_date.replace(year=start_date.year + 1)) & 
                              (df['LOCAL_DATE'] <= end_date.replace(year=end_date.year + 1))]

            u = filtered_df1['MEAN_TEMPERATURE_' + city]
            v = filtered_df2['MEAN_TEMPERATURE_' + city]
            
            # Calculer la corrélation
            corr = np.corrcoef(u, v)[0, 1]
            corrs.append(corr)
            
            start_date = start_date.replace(year=start_date.year + 1)
            end_date = end_date.replace(year=end_date.year + 1)
        

        for i in range(80):  # Comparer sur 80 cycles (années)
            # Filtrer les lignes entre start_date et end_date
            filtered_df1 = df[(df['LOCAL_DATE'] >= start_date) & (df['LOCAL_DATE'] <= end_date)]
            filtered_df2 = df[(df['LOCAL_DATE'] >= start_date.replace(year=start_date.year + 1)) & 
                            (df['LOCAL_DATE'] <= end_date.replace(year=end_date.year + 1))]

            # Vérifier que les DataFrames ne sont pas vides
            if filtered_df1.empty or filtered_df2.empty:
                print(f"Aucune donnée pour l'intervalle {start_date} - {end_date}.")
                start_date = start_date.replace(year=start_date.year + 1)
                end_date = end_date.replace(year=end_date.year + 1)
                continue

            # Extraire les températures et aligner sur les mêmes index de date
            u = filtered_df1.set_index('LOCAL_DATE')['MEAN_TEMPERATURE_' + city].dropna()
            v = filtered_df2.set_index('LOCAL_DATE')['MEAN_TEMPERATURE_' + city].dropna()

            # Aligner les séries sur les mêmes dates
            aligned_u, aligned_v = u.align(v, join='inner')

            # Vérifier que les séries alignées ne sont pas vides
            if len(aligned_u) == 0 or len(aligned_v) == 0:
                print(f"Séries alignées vides pour {city} entre {start_date} et {end_date}.")
                start_date = start_date.replace(year=start_date.year + 1)
                end_date = end_date.replace(year=end_date.year + 1)
                continue

            # Calculer la corrélation
            corr = np.corrcoef(aligned_u, aligned_v)[0, 1]
            corrs.append(corr)

            # Passer à l'année suivante
            start_date = start_date.replace(year=start_date.year + 1)
            end_date = end_date.replace(year=end_date.year + 1)


        city_corr.append(corrs)
    correlations_per_city[city] = city_corr

# Initialiser Dash
app = Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1("Corrélation des températures par ville et saison"),
    dcc.Dropdown(
        id='city-dropdown',
        options=[{'label': city, 'value': city} for city in city_list],
        value='CALGARY'
    ),
    dcc.Graph(id='correlation-graph')
])

# Callback pour mettre à jour le graphique
@app.callback(
    Output('correlation-graph', 'figure'),
    [Input('city-dropdown', 'value')]
)
def update_graph(selected_city):
    data = correlations_per_city[selected_city]
    figure = {
        'data': [
            {'x': list(range(len(corr))), 'y': corr, 'type': 'line', 'name': season}
            for corr, season in zip(data, seasons)
        ],
        'layout': {
            'title': f'Corrélations des températures pour {selected_city}',
            'xaxis': {'title': 'Années depuis 1940'},
            'yaxis': {'title': 'Corrélation'},
            'legend': {'title': 'Saisons'},
            'grid': True
        }
    }
    return figure

# Lancer l'application
if __name__ == '__main__':
    app.run_server(debug=True)
