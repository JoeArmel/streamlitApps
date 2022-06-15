import streamlit as st
from PIL import Image
import pandas as pd
import base64
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests
import json
import time

# -----------------------------------------------------------------------------------%

# Mise en Page
## page expand to full (Affichage de la page en plein écran)
st.set_page_config(layout="wide")

# Titre
img = Image.open("logo.png", "r")

st.image(img, caption='Bitcoin golden image', width=None)
st.title('Prix Crypto Monnaie')
st.markdown("""
Cette application récupère le prix des top 100 crypto monnaies à partir des données disponoibles sur **CoinMarketCap**! 
""")

# A propos
expander_bar = st.expander("A propos...")
expander_bar.markdown("""
* **Librairies Python:** base64, Pandas, streamlit, numpy, matplotlib, requests, Beautifullsoup, json, time, PIL
* **Source des données:** [CoinMarketCap](https://coinmarketcap.com/).
* **Credit:** Web scraping adapté à partir de l'article *[Web Scraping Crypto Prices With Python]
(https://bryanf.medium.com/web-scraping-crypto-prices-with-python-41072ea5b5bf)* publié 
par *[Bryan Feng](https://bryanf.medium.com/?source=post_page-----41072ea5b5bf--------------------------------)* 
sur Medium.
""")

# Mise en page
## Division de la page en 3 colonnes (col1 = sidebar, col2 et col3 = page principale)
col1 = st.sidebar
col2, col3 = st.columns((2, 1))
# largeur_col2 =  2*largeur_col3

# Sidebar + Feuille Principale
col1.header('Paramètres de sélection')

# Selection de l'unité monétaire
currency_price_unit = col1.selectbox("Sélectionner la devise", ['USD', 'ETH', 'BTC'])


# Web scraping des données sur CoinMarketCap.
@st.cache
def load_data():
    url = "https://coinmarketcap.com"
    cmc = requests.get(url)
    soup = BeautifulSoup(cmc.content, 'html.parser')

    data = soup.find('script', id='__NEXT_DATA__', type='application/json')
    coins = {}
    coin_data = json.loads(data.contents[0])
    listings = coin_data['props']['initialState']['cryptocurrency']['listingLatest']['data']
    for i in listings:
        coins[str(i['id'])] = i['slug']
        
    nom = []
    accronyme = []
    capitalisation = []
    taux_change_1h = []
    taux_change_24h = []
    taux_change_7j = []
    prix = []
    volume_24h = []

    for i in listings:
        nom.append(i['slug'])
        accronyme.append(i['symbol'])
        prix.append(i['quote'][currency_price_unit]['price'])
        taux_change_1h.append(i['quote'][currency_price_unit]['percentChange1h'])
        taux_change_24h.append(i['quote'][currency_price_unit]['percentChange24h'])
        taux_change_7j.append(i['quote'][currency_price_unit]['percentChange7d'])
        capitalisation.append(i['quote'][currency_price_unit]['marketCap'])
        volume_24h.append(i['quote'][currency_price_unit]['volume24h'])

    df = pd.DataFrame(
        columns=['nom', 'accronyme', 'capitalisation', 'taux_change_1h', 'taux_change_24h', 'taux_change_7j', 'prix',
                 'volume_24h'])
    df['nom'] = nom
    df['accronyme'] = accronyme
    df['capitalisation'] = capitalisation
    df['taux_change_1h'] = taux_change_1h
    df['taux_change_24h'] = taux_change_24h
    df['taux_change_7j'] = taux_change_7j
    df['prix'] = prix
    df['volume_24h'] = volume_24h
    return df


# Chargement des données dans la variable dataframe nommée df
df = load_data()

## Sidebar - Sélection des crypto monnaies
sorted_coin = sorted(df['accronyme'])
selected_coin = col1.multiselect('Crypto monnaies', sorted_coin, sorted_coin)

# Filtrage des données en fonction des crypto monnaies séléctionnées
df_selected_coin = df[(df['accronyme'].isin(selected_coin))]

## Sidebar - Nombre de monnaies affichées
num_coin = col1.slider('Affichage du Top N crypto monnaies', 1, 100, 100)
df_coins = df_selected_coin[:num_coin]

## Sidebar - Taux de change par période de temps
taux_change = col1.selectbox('Taux de change sur une période de :', ['1h', '24h', '7j'])
dico_taux = {'1h': 'taux_change_1h', '24h': 'taux_change_24h', '7j': 'taux_change_7j'}
selection_taux_period = dico_taux[taux_change]

## Sidebar - Option de tri des valeurs
tri_valeurs = col1.selectbox('Trier les valeurs?', ['Oui', 'Non'])

col2.subheader('Tableau des prix des crypto-monnaies sélectionnées ')
col2.write('Taille des données: ' + str(df_selected_coin.shape[0]) + ' lignes et ' +
           str(df_selected_coin.shape[1]) + ' colonnes.')

# Affichage du dataframe via streamlit
col2.dataframe(df_coins)


# Téléchargement des données en format CSV
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="Cryptocurrency.csv">Télécharger le Fichier CSV</a>'
    return href


st.markdown(filedownload(df_selected_coin), unsafe_allow_html=True)

# Préparation des données pour le bar plot
col2.subheader('Tableau des prix de change')
df_change = pd.concat([df_coins.accronyme, df_coins.taux_change_1h, df_coins.taux_change_24h, df_coins.taux_change_7j],
                      axis=1)
df_change = df_change.set_index('accronyme')
df_change['taux_positif_1h'] = df_change['taux_change_1h'] > 0
df_change['taux_positif_24h'] = df_change['taux_change_24h'] > 0
df_change['taux_positif_7j'] = df_change['taux_change_7j'] > 0

# Affichage du dataframe via streamlit
col2.dataframe(df_change)

# Création des Bar plot en fonction de la période choise

col3.subheader('Bar plot du prix de change')

if taux_change == '7j':
    if tri_valeurs == 'Oui':
        df_change = df_change.sort_values(by=['taux_change_7j'])
    col3.write('*Variations du taux de change sur 7 jours*')
    plt.figure(figsize=(5, 15))
    plt.subplots_adjust(top=1, bottom=0)
    df_change['taux_change_7j'].plot(kind='barh', color=df_change.taux_positif_7j.map({True: 'g', False: 'r'}))
    col3.pyplot(plt)
elif taux_change == '24h':
    if tri_valeurs == 'Oui':
        df_change = df_change.sort_values(by=['taux_change_24h'])
    col3.write('*Variations du taux de change sur 24 heures*')
    plt.figure(figsize=(5, 15))
    plt.subplots_adjust(top=1, bottom=0)
    df_change['taux_change_24h'].plot(kind='barh', color=df_change.taux_positif_7j.map({True: 'g', False: 'r'}))
    col3.pyplot(plt)
else:
    if tri_valeurs == 'Oui':
        df_change = df_change.sort_values(by=['taux_change_1h'])
    col3.write('*Variations du taux de change par heure*')
    plt.figure(figsize=(5, 15))
    plt.subplots_adjust(top=1, bottom=0)
    df_change['taux_change_1h'].plot(kind='barh', color=df_change.taux_positif_7j.map({True: 'g', False: 'r'}))
    col3.pyplot(plt)
