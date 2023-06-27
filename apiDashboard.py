import streamlit as st
import requests
import plotly.graph_objects as go

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
                st.write(probabilities)

                # Vérifier si la probabilité est supérieure à 0.5
                if probabilities[0][0] > 0.5:  # Accéder à la valeur de probabilité
                    st.write("Le crédit est accepté", probabilities[0][0])
                else:
                    st.write("Le crédit est refusé", probabilities[0][1])

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
                    title='Top 4 des fonctionnalités SHAP',
                    xaxis_title='Fonctionnalités',
                    yaxis_title='Valeurs SHAP'
                )
                st.plotly_chart(fig_top_4)

                # Envoyer une requête POST à l'API Flask pour obtenir les données de distribution totale
                url_distribution = 'http://creepzy.pythonanywhere.com/all_data'
                response_distribution = requests.post(url_distribution)
                if response_distribution.status_code == 200:
                    data_distribution = response_distribution.json()

                    # Récupérer les noms et valeurs des fonctionnalités de distribution totale
                    distribution_features = data_distribution.get('Fonctionnalités')
                    distribution_values = data_distribution.get('Distribution totale')

                   # Récupérer les valeurs SHAP du client sélectionné
                    selected_shap_values = data_client.values()

                    # Convertir selected_shap_values en liste
                    selected_shap_values = list(selected_shap_values)

                    # Créer la figure avec la distribution totale et la valeur SHAP du client sélectionné
                    fig_distribution = go.Figure()

                    # Vérifier si les valeurs de distribution sont disponibles
                    if distribution_values is not None:
                        # Ajouter les points de la distribution totale des valeurs SHAP par rapport aux 4 meilleures fonctionnalités
                        for feature, value in zip(top_4_features, distribution_values):
                            fig_distribution.add_trace(go.Box(y=value, name=feature, boxpoints='all', jitter=0.5, pointpos=-2))

                    # Ajouter les points du client sélectionné en bleu
                    fig_distribution.add_trace(go.Scatter(x=top_4_features, y=top_4_values, mode='markers', name='Client sélectionné', marker=dict(color='blue')))

                    # Ajouter les valeurs globales des 4 fonctionnalités en rouge
                    fig_distribution.add_trace(go.Scatter(x=top_4_features, y=selected_shap_values, mode='markers', name='Valeurs globales', marker=dict(color='red')))

                    fig_distribution.update_layout(
                        title='Positionnement du client par rapport à la distribution totale',
                        xaxis_title='Fonctionnalités',
                        yaxis_title='Valeurs SHAP',
                        legend=dict(orientation='h')  # Placer la légende horizontalement
                    )

                    st.plotly_chart(fig_distribution)


