import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

st.title('USA-NFL : Stats des Joueurs de Football')

st.markdown("""
Cette application effectue un webscraping des données statistiques des joueurs évoluant en Ligue Nationale de Football 
(NFL) aux USA.
* **Librairies Python:** base64, Pandas, streamlit, numpy, matplotlib, seaborn
* **Source des données:** [pro-football-reference.com](https://www.pro-football-reference.com/).
""")

st.sidebar.header('Paramètres de sélection')
selected_year = st.sidebar.selectbox('Année', list(reversed(range(1990, 2021))))


# Web scraping des stats des joueurs de NBA
# https://www.pro-football-reference.com/years/2019/rushing.htm


@st.cache
def load_data(year):
    url = "https://www.pro-football-reference.com/years/" + str(year) + "/rushing.htm"
    html = pd.read_html(url, header=1)
    df = html[0]
    raw = df.drop(df[df.Age == 'Age'].index)
    raw = raw.fillna(0)
    to_replace = {
        'Pos': {'rb': 'RB', '/rb': 'RB', 'wr': 'WR', '/wr': 'WR', 'qb': 'QB', '/qb': 'QB', '/fb': 'FB', 'fb': 'FB',
                'te': 'TE', 'ss': 'SS'}}

    raw.replace(to_replace, inplace=True)
    return raw.drop(['Rk'], axis=1)


playerstats = load_data(selected_year)
# poste = playerstats.Pos.unique().T
# poste

# Sidebar - Team selection
sorted_unique_team = sorted(playerstats.Tm.unique())
selected_team = st.sidebar.multiselect('Equipe(s)', sorted_unique_team, sorted_unique_team)

# Sidebar - Position selection
unique_pos = ['RB', 'QB', 'WR', 'FB', 'TE', 'FS', 'LG', 'SS']
selected_pos = st.sidebar.multiselect('Poste', unique_pos, unique_pos)

# Filtering data

df_selected_team = playerstats[(playerstats.Tm.isin(selected_team)) & (playerstats.Pos.isin(selected_pos))]

st.subheader('Acronyme des postes avec description')
st.markdown("""
RB : Running-back                       \n
QB : Quarterback                        \n
WR : Wide receiver                      \n
FB : Fullback                           \n
TE : Tight end                          \n
SS : Strong safety                      \n
FS : Free safety
""")

st.header('Stats de Joueurs pour Equipe(s) Sélctionnée(s)')
st.write('Dimension des données: ' + str(df_selected_team.shape[0]) + ' lignes et ' + str(df_selected_team.shape[1]) + ' colonnes.')
st.write('La saison ' + str(selected_year) + ' a vu la participation de ' + str(len(df_selected_team.Player.unique())) +
         ' joueurs pour ' + str(len(df_selected_team.Tm.unique())) + ' équipes sélectionnées.' )
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
    mask[np.triu_indices_from(mask)] = True
    with sns.axes_style("white"):
        f, ax = plt.subplots(figsize=(7, 5))
        ax = sns.heatmap(corr, mask=mask, vmax=1, square=True)
    st.pyplot(f)