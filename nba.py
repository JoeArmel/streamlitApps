import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

st.title('Statistiques des Joueurs de NBA')

st.markdown("""
Cette application effectue un webscraping des données statistiques des joueurs évoluant en NBA.
* **Librairies Python :** base64, Pandas, streamlit, numpy, matplotlib, seaborn
* **Source des données :** [Basketball-reference.com](https://www.basketball-reference.com/).
""")

st.sidebar.header('Paramètres de sélection')
selected_year = st.sidebar.selectbox('Année', list(reversed(range(1950, 2020))))

# Web scraping des stats des joueurs de NBA
# https://www.basketball-reference.com/leagues/NBA_year_per_game.html

@st.cache
def load_data(year):
    url = "https://www.basketball-reference.com/leagues/NBA_" + str(year) + "_per_game.html"
    html = pd.read_html(url, header=0)
    df = html[0]
    raw = df.drop(df[df.Age == 'Age'].index)
    raw = raw.fillna(0)
    return raw.drop(['Rk'], axis=1)


playerstats = load_data(selected_year)

# Sidebar - Team selection
sorted_unique_team = sorted(playerstats.Tm.unique())
selected_team = st.sidebar.multiselect('Equipe(s)', sorted_unique_team, sorted_unique_team)

# Sidebar - Position selection
unique_pos = ['C', 'PF', 'SF', 'PG', 'SG']
selected_pos = st.sidebar.multiselect('Poste', unique_pos, unique_pos)

# Filtering data
df_selected_team = playerstats[(playerstats.Tm.isin(selected_team)) & (playerstats.Pos.isin(selected_pos))]

st.subheader('Acronyme des postes avec description')
st.markdown("""
PG : Meneur (point guard)\n
SG : Arrière (shooting guard)\n
SF : Ailier (small forward)\n
PF : Ailier fort (power forward)\n
C : Pivot (center)""")

st.header('Stats de Joueurs pour Equipe(s) Sélctionnée(s)') #Affichage des stats des joueurs pour l(es) équipe(s) Sélctionnée(s)
st.write('Dimension des données: ' + str(df_selected_team.shape[0]) + ' lignes et ' + str(df_selected_team.shape[1]) + ' colonnes.')
st.dataframe(df_selected_team)

# Download NBA player Stats data
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Télécharger le Fichier CSV</a>'
    return href

st.markdown(filedownload(df_selected_team), unsafe_allow_html=True)

# Heatmap
if st.button('Matrice Heatmap'):
    st.header('Matrice Heatmap d\'Inter-corrélation')
    df_selected_team.to_csv('output.csv', index=False)
    df = pd.read_csv('output.csv')

    corr = df.corr()
    mask = np.zeros_like(corr)
    mask[np.tril_indices_from(mask)] = True
    with sns.axes_style("white"):
        f, ax = plt.subplots(figsize=(7, 5))
        ax = sns.heatmap(corr, mask=mask, vmax=1, square=True)
    st.pyplot(f)