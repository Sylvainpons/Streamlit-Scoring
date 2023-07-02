import streamlit as st
import requests
import plotly.graph_objects as go
import numpy as np

st.title('Dashboard de notation du modèle')

# Envoyer une requête GET à l'API Flask pour obtenir la liste des IDs
response = requests.get('http://creepzy.pythonanywhere.com/ids')
if response.status_code == 200:
    data = response.json()
    ids = data.get('ids')
    ids = ids[:10000]  # Limitez aux 10 000 premiers ID clients

    if ids:
        selected_id = st.selectbox('Sélectionnez un ID client', ids)

        # Vérifier si un ID client est sélectionné
        if selected_id:
            # Envoyer une requête POST à l'API Flask pour obtenir les probabilités prédites
            url = 'http://creepzy.pythonanywhere.com/predict'
            payload = {'id_client': selected_id}
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                probabilities = data.get('probabilities')
                

                # Vérifier si la probabilité est supérieure à 0.5
                if probabilities[0][0] > 0.5:  # Accéder à la valeur de probabilité
                    st.write("Le crédit est accepté, la probabilité d'un remboursement est de ", round(probabilities[0][0],2),"%")
                else:
                    st.write("Le crédit est refusé, la probalité qu'il ne rembourse pas est de ", round(probabilities[0][1],2),"%")

            # Envoyer une autre requête POST à l'API Flask pour obtenir les données du client sélectionné
            url_data = 'http://creepzy.pythonanywhere.com/data'
            payload_data = {'id_client': selected_id}
            response_data = requests.post(url_data, json=payload_data)
            if response_data.status_code == 200:
                data_client = response_data.json()

                # Récupérer les noms et valeurs des 4 meilleures fonctionnalités SHAP
                top_4_features = sorted(data_client, key=data_client.get, reverse=True)[:4]
                top_4_values = [data_client[feature] for feature in top_4_features]

                # Créer un graphique en barres pour les 4 meilleures fonctionnalités SHAP
                fig_top_4 = go.Figure(data=go.Bar(x=top_4_features, y=top_4_values))
                fig_top_4.update_layout(
                    title='Top 4 des principales caractéristiques influentes',
                    xaxis_title='Fonctionnalités',
                    yaxis_title='Valeurs'
                )
                st.plotly_chart(fig_top_4)
                
 # Récupérer les valeurs correspondantes dans X_train pour les fonctionnalités du top_4_features
    x_train_response = requests.get('http://creepzy.pythonanywhere.com/x_train')

    if x_train_response.status_code == 200:
        dataX = x_train_response.json()
        X_train = dataX.get('x_train')

        # Créer une liste des valeurs correspondantes dans X_train pour les fonctionnalités du top_4_features
        x_train_values = [np.mean([x_train[feature] for x_train in X_train]) for feature in top_4_features]


        # Ajouter la valeur du client sélectionné à la liste des valeurs de X_train
        x_train_values.append(top_4_values)

        # Créer un graphique en barres pour les valeurs du client sélectionné et de X_train
        fig_top_4 = go.Figure()
        fig_top_4.add_trace(go.Bar(x=top_4_features, y=top_4_values, name='Client sélectionné'))
        fig_top_4.add_trace(go.Bar(x=top_4_features, y=x_train_values, name='Valeur moyenne des clients',marker=dict(color='red')))
        fig_top_4.update_layout(
            title='Comparaison des valeurs du client',
            xaxis_title='Caractéristiques',
            yaxis_title='Valeurs'
        )
        st.plotly_chart(fig_top_4)
