import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import yfinance as yf

st.title('Standard and Poor\'s 500 App')

st.markdown("""
\n
Cette application récupère de Wikipedia, la liste des entreprises ou compagnies appartenant à **S&P 500** et 
leur **cours à la fermeture (stock closing price)** (year-to-date)!
* **Librairies Python:** base64, Pandas, streamlit, numpy, matplotlib, seaborn, yfinance
* **Source des données:** [Wikipedia](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies).
""")

st.sidebar.header('Paramètres de sélection')
#selected_year = st.sidebar.selectbox('Année', list(reversed(range(1990, 2021))))


# Web scraping des données sur S&P 500.
# https://en.wikipedia.org/wiki/List_of_S%26P_500_companies

@st.cache
def load_data():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    html = pd.read_html(url, header=0)
    return html[0]


# Chargement des données dans la variable nommée df
df = load_data()

# Regroupement des entreprises par secteur d'activité
# GICS sector =  Global Industry Classification Sector
sector = df.groupby('GICS Sector')

# Sidebar - Sector selection -- Box pour la sélection du secteur d'activité
sorted_unique_sector = sorted(df['GICS Sector'].unique())
selected_sector = st.sidebar.multiselect('Secteur d\'activité', sorted_unique_sector, sorted_unique_sector)

# Filtering data
df_selected_sector = df[(df['GICS Sector'].isin(selected_sector))]

st.header('Entrepises par secteur(s) sélctionnée(s)')
st.write('Taille des données: ' + str(df_selected_sector.shape[0]) + ' lignes et ' +
         str(df_selected_sector.shape[1]) + ' colonnes.')
st.dataframe(df_selected_sector)


# Download S&P 500 data
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="SP500.csv">Télécharger le Fichier CSV</a>'
    return href


st.markdown(filedownload(df_selected_sector), unsafe_allow_html=True)

# https://pypi.org/project/yfinance/

data = yf.download(
    tickers=list(df_selected_sector[:10].Symbol),
    period="ytd",
    interval="1d",
    group_by="ticker",
    auto_adjust=True,
    prepost=True,
    threads=True,
    proxy=None
)

# Graphique du cours à la fermeture (Closing Price) des Symboles requetés () Query Symbol.
def price_plot(symbol):
    df = pd.DataFrame(data[symbol].Close)
    df['Date'] = df.index
    f, ax=plt.subplots()
    plt.fill_between(df.Date, df.Close, color='skyblue', alpha=0.4)
    plt.plot(df.Date, df.Close, color='skyblue', alpha=0.9)
    plt.xticks(rotation=90)
    plt.title(symbol, fontweight='bold')
    plt.xlabel('Date', fontweight='bold')
    plt.ylabel('Closing Price', fontweight='bold')
    return st.pyplot(f)


num_company = st.sidebar.slider('Nombre d\'entreprises', 1, 10)

if st.button('Visualier les cours'):
    st.header('Cours des prix à la clôture') # Stock closing Price
    for i in list(df_selected_sector.Symbol)[:num_company]:
        price_plot(i)


# Heatmap
#if st.button('Matrice Heatmap'):
#    st.header('Matrice Heatmap d\'Inter-corrélation')
#    df_selected_team.to_csv('output.csv', index=False)
#    df = pd.read_csv('output.csv')

 #   corr = df.corr()
 #   mask = np.zeros_like(corr)
 #   mask[np.triu_indices_from(mask)] = True
 #   with sns.axes_style("white"):
 #       f, ax = plt.subplots(figsize=(7, 5))
 #       ax = sns.heatmap(corr, mask=mask, vmax=1, square=True)
 #   st.pyplot(f)
