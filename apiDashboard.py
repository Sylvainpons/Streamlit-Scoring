import streamlit as st
import requests
import plotly.graph_objects as go

st.title('Dashboard de notation du modèle')

# Envoyer une requête GET à l'API Flask pour obtenir la liste des IDs
response = requests.get('http://localhost:5000/ids')
if response.status_code == 200:
    data = response.json()
    ids = data.get('ids')
    ids = ids[:10000]  # Limitez aux 10 000 premiers ID clients

    if ids:
        selected_id = st.selectbox('Sélectionnez un ID client', ids)

        # Vérifier si un ID client est sélectionné
        if selected_id:
            # Envoyer une requête POST à l'API Flask pour obtenir les probabilités prédites
            url = 'http://localhost:5000/predict'
            payload = {'id_client': selected_id}
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                probabilities = data.get('probabilities')
                st.write(probabilities)
                 # Vérifier si la probabilité est supérieure à 0.5
                if probabilities[0][0] > 0.5:  # Accéder à la valeur de probabilité
                    st.write("Le crédit est accepté",probabilities[0][0])
                else:
                    st.write("Le crédit est refusé",probabilities[0][1])

# Envoyer une autre requête POST à l'API Flask pour obtenir les données du client sélectionné
url_data = 'http://localhost:5000/data'
payload_data = {'id_client': selected_id}
response_data = requests.post(url_data, json=payload_data)
if response_data.status_code == 200:
    data_client = response_data.json()

    # Récupérer les noms et valeurs des 4 meilleures fonctionnalités SHAP
    top_4_features = sorted(data_client, key=data_client.get, reverse=True)[:4]
    top_4_values = [data_client[feature] for feature in top_4_features]

    # Créer un graphique en barres pour les 4 meilleures fonctionnalités SHAP
    fig = go.Figure(data=go.Bar(x=top_4_features, y=top_4_values))
    fig.update_layout(
        title='Top 4 des fonctionnalités SHAP',
        xaxis_title='Fonctionnalités',
        yaxis_title='Valeurs SHAP'
    )
    st.plotly_chart(fig)

                        
