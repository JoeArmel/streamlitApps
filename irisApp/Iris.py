import streamlit as st
import pandas as pd
from PIL import Image
from sklearn import datasets
from sklearn.ensemble import RandomForestClassifier

col1, col2 = st.columns((1, 6))


image = Image.open('irisApp/irislogo.jpg')
col1.image(image, width=None)


col2.title('App de Prédiction de Fleurs d’Iris')

st.write("""Cette App effectue une prédiction simple du type de **fleurs d'Iris**. 
""")
st.header("Informations Générales sur les Données Iris")

st.markdown("""L'ensemble de données contient 3 classes de 50 instances chacune, où chaque classe fait référence à un 
type de plante d'iris.
* **Objectif:** Prédire la classe d'une fleur d'iris à partir de certaines caractéristiques
* **Caractéristiques:** longueur_sépale, longueur_pétale, largeur_sépale, largeur_pétale en cm.
* **Classes:** Iris Setosa, Iris Versicolor, Iris Virginica  
'""")

st.sidebar.header("Paramètres Input Utilisateur")

def user_input_features():
    sepal_length = st.sidebar.slider('Longueur Sépales:', 2.5, 7.9, 3.0)
    sepal_width = st.sidebar.slider('Largeur Sépales:', 2.0, 4.5, 2.4)
    petal_length = st.sidebar.slider('Longueur Pétales:', 1.0, 7.5, 3.4)
    petal_width = st.sidebar.slider('Largeur Pétales:', 0.5, 6.5, 0.8)
    data = {
        'longueur_sépale': sepal_length,
        'largeur_sépale': sepal_width,
        'longueur_pétale': petal_length,
        'largeur_pétale': petal_width,
    }
    features = pd.DataFrame(data, index=[0])
    return features

df = user_input_features()

st.subheader("Paramètres Input Utilisateur")
st.write(df)

iris = datasets.load_iris()
X = iris.data
Y = iris.target

rfc = RandomForestClassifier()
rfc.fit(X, Y)

prediction = rfc.predict(df)
prediction_proba = rfc.predict_proba(df)

st.subheader('Labels des Classes et Indices Correspondants')
st.write(iris.target_names)

st.subheader('Prédictions')
st.write(iris.target_names[prediction])


st.subheader('Probabilité des Prédictions')
st.write(prediction_proba)
