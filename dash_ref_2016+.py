import pandas as pd
import numpy as np
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from datetime import datetime

# Charger le DataFrame depuis un fichier CSV (à ajuster selon votre chemin de fichier)
df = pd.read_csv('canadian_climate_change_history_updated.csv')

# Convertir la colonne 'LOCAL_DATE' en datetime
df['LOCAL_DATE'] = pd.to_datetime(df['LOCAL_DATE'], format='%d-%b-%Y %H:%M:%S')

# Liste des villes pour le dropdown
city_list = ["CALGARY", "OTTAWA", "TORONTO", "VANCOUVER", "WINNIPEG"]

# Initialiser l'application Dash
app = dash.Dash(__name__)

# Layout de l'application
app.layout = html.Div([
    html.H1("Analyse des températures par ville et par saison", style={'textAlign': 'center'}),
    
    # Dropdown pour sélectionner une ville
    html.Div([
        html.Label("Sélectionnez une ville :"),
        dcc.Dropdown(
            id='city-dropdown',
            options=[{'label': city, 'value': city} for city in city_list],
            value='CALGARY',  # Valeur par défaut
            clearable=False
        ),
    ], style={'width': '50%', 'margin': 'auto'}),
    
    # Graphique interactif
    dcc.Graph(id='temperature-graph'),

    # Graphique des divergences
    dcc.Graph(id='divergence-graph')
])

# Callback pour mettre à jour les graphiques en fonction de la ville sélectionnée
@app.callback(
    [Output('temperature-graph', 'figure'),
     Output('divergence-graph', 'figure')],
    [Input('city-dropdown', 'value')]
)
def update_graph(selected_city):
    # Filtrer les colonnes pour la ville sélectionnée
    temperature_col = f"MEAN_TEMPERATURE_{selected_city}"
    
    # Préparer le graphique des températures
    temperature_figure = {
        'data': [
            go.Scatter(
                x=df['LOCAL_DATE'],
                y=df[temperature_col],
                mode='lines',
                name=f'Température moyenne ({selected_city})'
            )
        ],
        'layout': {
            'title': f'Température moyenne à {selected_city} sur le temps',
            'xaxis': {'title': 'Date'},
            'yaxis': {'title': 'Température (°C)'},
            'template': 'plotly_white'
        }
    }

    # Calcul des divergences par saison pour la ville sélectionnée
    seasons = ["spring", "summer", "autumn", "winter"]
    divergence_data = []
    years = range(1940, 1940 + 80)
    
    def get_interval_ref(season): # marge de 15j de chaque coté
        res = []
        if season == "spring":
            res = [[datetime(2015, 3, 15),datetime(2015, 5, 15)],
                   [datetime(2016, 3, 15),datetime(2016, 5, 15)],
                   [datetime(2017, 3, 15),datetime(2017, 5, 15)]]
            
        if season == "summer":
            res = [[datetime(2015, 6, 15),datetime(2015, 8, 15)],
                  [datetime(2016, 6, 15),datetime(2016, 8, 15)],
                  [datetime(2017, 6, 15),datetime(2017, 8, 15)]]
        if season == "autumn":
            res = [[datetime(2015, 9, 15),datetime(2015, 11, 15)],
                   [datetime(2016, 9, 15),datetime(2016, 11, 15)],
                   [datetime(2017, 9, 15),datetime(2017, 11, 15)]]
        if season == "winter":
            res = [[datetime(2015, 12, 15),datetime(2016, 2, 15)],
                   [datetime(2016, 12, 15),datetime(2017, 2, 15)],
                   [datetime(2017, 12, 15),datetime(2018, 2, 15)]]
        return res

    
    for season in seasons:
        start_date, end_date = get_interval(season)
        start_date = start_date.replace(year=1940)
        end_date = end_date.replace(year=1941 if season == "winter" else 1940)

        start_date_ref_2015 = get_interval_ref(season)[0][0]
        start_date_ref_2016 = get_interval_ref(season)[1][0]
        start_date_ref_2017 = get_interval_ref(season)[2][0]

        end_date_ref_2015 = get_interval_ref(season)[0][1]
        end_date_ref_2016 = get_interval_ref(season)[1][1]
        end_date_ref_2017 = get_interval_ref(season)[2][1]

        filtered_df_ref = df[
                            (df['LOCAL_DATE'] >= start_date_ref_2015) & (df['LOCAL_DATE'] <= end_date_ref_2015) | 
                            (df['LOCAL_DATE'] >= start_date_ref_2016) & (df['LOCAL_DATE'] <= end_date_ref_2016) |
                            (df['LOCAL_DATE'] >= start_date_ref_2017) & (df['LOCAL_DATE'] <= end_date_ref_2017)]
        
        season_divergences = []
        for year in years:
            filtered_df1 = df[
                            (df['LOCAL_DATE'] >= start_date) & (df['LOCAL_DATE'] <= end_date) | 
                            (df['LOCAL_DATE'] >= start_date.replace(year=end_date.year + 1)) & (df['LOCAL_DATE'] <= end_date.replace(year=end_date.year + 1)) |
                            (df['LOCAL_DATE'] >= start_date.replace(year=end_date.year + 2)) & (df['LOCAL_DATE'] <= end_date.replace(year=end_date.year + 2))]
            
            u = filtered_df1[temperature_col]
            v = filtered_df_ref[temperature_col]

            m1 = np.mean(u)
            v1 = np.var(u, ddof=1)
            m2 = np.mean(v)
            v2 = np.var(v, ddof=1)

            d = (1/2) * ((m1 - m2) ** 2 / (v1 + v2)) + (1/2) * ((v2 / v1) + (v1 / v2)) - 1
            season_divergences.append(d)
            
            start_date = start_date.replace(year=start_date.year + 1)
            end_date = end_date.replace(year=end_date.year + 1)

        divergence_data.append(go.Scatter(
            x=list(years),
            y=season_divergences,
            mode='lines',
            name=season
        ))

    # Préparer le graphique des divergences
    divergence_figure = {
        'data': divergence_data,
        'layout': {
            'title': f'Divergences pour les saisons à {selected_city}',
            'xaxis': {'title': 'Années'},
            'yaxis': {'title': 'Divergence'},
            'template': 'plotly_white'
        }
    }

    return temperature_figure, divergence_figure

def get_interval_(season): # sans marge
    res = ""
    if season == "spring":
        res = [datetime(1940, 3, 1),datetime(1940, 5, 31)]
    if season == "summer":
        res = [datetime(1940, 6, 1),datetime(1940, 8, 31)]
    if season == "autumn":
        res = [datetime(1940, 9, 1),datetime(1940, 11, 30)]
    if season == "winter":
        res = [datetime(1940, 12, 1),datetime(1940, 2, 28)]
    return res


def get_interval(season): # marge de 15j de chaque coté
    res = ""
    if season == "spring":
        res = [datetime(1940, 3, 15),datetime(1940, 5, 15)]
    if season == "summer":
        res = [datetime(1940, 6, 15),datetime(1940, 8, 15)]
    if season == "autumn":
        res = [datetime(1940, 9, 15),datetime(1940, 11, 15)]
    if season == "winter":
        res = [datetime(1940, 12, 15),datetime(1940, 2, 15)]
    return res


# Exécuter l'application
if __name__ == '__main__':
    app.run_server(debug=True)
