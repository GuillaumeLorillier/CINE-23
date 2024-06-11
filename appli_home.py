import streamlit as st
import requests
import pandas as pd
import random
import time
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from fonctions import *
from st_clickable_images import clickable_images

st.set_page_config(layout="wide")

api_key = "f0b18a4d80528e86c179f4f51f4aa4b4" 

# Ajouter la feuille de style CSS
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Ajouter le titre de l'application
st.markdown('<h1>Cinéma 23</h1>', unsafe_allow_html=True)

logo_path = r"C:\Document\Python\Projet\Projet_2\.streamlit\media\logo_transparent.png"

# Charger les données
df = pd.read_csv('C:/Document/Python/Projet/Projet_2/.streamlit/data_final.csv')  

# Colonnes numériques à utiliser pour le modèle KNN
numerical_columns = ['runtimeMinutes', 'averageRating', 'numVotes', 'year',
                     'Horror', 'Crime', 'Thriller', 'Music', 'Mystery', 'Musical', 'Drama',
                     'Sport', 'Documentary', 'Western', 'News', 'Romance', 'Comedy', 'History', 'War',
                     'Adventure', 'Animation', 'Biography', 'Action', 'Sci-Fi', 'Family', 'Fantasy']

data_numeric = df[numerical_columns]

# Normalisation des données avec StandardScaler
scaler = StandardScaler()
data_normalized = scaler.fit_transform(data_numeric)

# Chargement du modèle KNN
knn = NearestNeighbors(n_neighbors=12)
knn.fit(data_normalized)

# URL de base pour les affiches de films
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500/"

# Liste des colonnes de genres disponibles
genres_available = ['Action', 'Animation', 'Adventure', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family', 'Fantasy',
                     'History', 'Horror',  'Music', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Sport', 'Thriller', 'War', 'Western']
                     
# Fonction pour trouver les films les plus proches en utilisant le titre du film
def find_closest_films_by_title(title_input, data_normalized, knn, data):
    # Filtrer les films qui contiennent le titre saisi (non sensible à la casse)
    filtered_data = data[data['title'].str.contains(title_input, case=False, na=False)]
    
    # Vérifier si des films correspondants ont été trouvés
    if not filtered_data.empty:
        # Utiliser la première ligne pour effectuer la recherche KNN
        index = filtered_data.index[0]
        
        # Trouver les films les plus proches de celui à l'index trouvé
        distances, indices = knn.kneighbors([data_normalized[index]])
        
        # Extraire les films les plus proches de `data`
        closest_films = data.iloc[indices[0]]
        return closest_films
    else:
        return pd.DataFrame()

# Initialiser l'état du film sélectionné
if 'selected_film' not in st.session_state:
    st.session_state.selected_film = None

year = df['year'].unique().tolist()
year.sort(reverse=True)

# Créez des onglets pour le filtre par genre et par année
tab_genre, tab_year, tab_search_movie = st.tabs(["Catégorie", "Année", 'Recherche de films'])

# Fonction pour afficher les détails du film
def afficher_details_film(film_details):
    if film_details:
        st.write(f"Title: {film_details.get('title')}")
        st.write(f"Overview: {film_details.get('overview')}")
        poster_path = film_details.get('poster_path')
        if poster_path:
            poster_url = IMAGE_BASE_URL + poster_path
            st.image(poster_url)
        st.write(f"Release Date: {film_details.get('release_date')}")
        st.write(f"Rating: {film_details.get('vote_average')}")



######################################################################################################## Onglet 'Genre'
with tab_genre:
    # Afficher les détails du film si un film est sélectionné
    if 'selected_film' in st.session_state and st.session_state.selected_film is not None:
    # Obtenir les détails du film depuis l'API TMDb
        film_details = get_film_details(st.session_state.selected_film, api_key)

        if film_details:
            poster_path = film_details.get('poster_path')
            overview = film_details.get('overview', "Synopsis non disponible")
            release_date = film_details.get('release_date')
            vote_average = film_details.get('vote_average')

            if vote_average is not None:
                vote_average = round(vote_average, 1)

            # Extraire l'année à partir de la date de sortie
            release_year = release_date[:4] if release_date else "Année inconnue"

            genres_data = film_details.get('genres', [])
 
            # Extraire le nom de chaque genre
            genre_names = [genre.get('name', '') for genre in genres_data]

            # Joindre les noms des genres en une seule chaîne de caractères
            genres_string = ', '.join(genre_names)
 
 
            # URL complète de l'affiche du film
            if poster_path:
                poster_url = IMAGE_BASE_URL + poster_path

                # Afficher les détails du film
                col1, col2, col3, col4 = st.columns([3, 2, 4, 1])

                with col1:
                    st.image(poster_url, width=400)

                with col2:
                    # Affichage du titre du film
                    st.markdown(
                        f"""
                        <div style='text-align: center; margin-bottom: 80px;'>
                            <h2>{film_details['title']}</h2>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    # Affichage des informations sur le film
                    st.markdown(
                        f"""
                        <div style='display: flex; justify-content: center; align-items: center; height: 100%; margin-bottom: 180px'>
                            <div style='text-align: center;'>
                                <p><strong style='color: #3ECDC5;'>Année de sortie :</strong> <span style='color: white;'>{release_year}</span></p>
                                <p><strong style='color: #3ECDC5;'>Note :</strong> <span style='color: white;'>{vote_average}</span></p>
                                <p><strong style='color: #3ECDC5;'>Genres :</strong> <span style='color: white;'>{genres_string}</span></p>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with col3:
                    # Affichage du synopsis du film
                    st.markdown(
                        f"""
                        <div style='display: flex; justify-content: center; align-items: center; height: 100%; margin-bottom: 180px'>
                            <div>
                                <h4>Synopsis :</h4>
                                <p>{overview}</p>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                # Bouton pour revenir à la sélection par genre
                if st.button("Retour", key="back_button_genre"):
                    del st.session_state.selected_film
                    st.experimental_rerun()
    else:
        # Afficher la sélection par genre
        # Créez trois colonnes avec les largeurs différentes pour la taille du selectbox
        col1, col2, col3 = st.columns([1, 1, 7])

        # Placez la selectbox dans la 1ère colonne
        with col1:
            selected_genre = st.selectbox("", genres_available)

        # Filtrer les films selon le genre sélectionné
        films_filtrés = df[df[selected_genre] == 1]

        # Trier les films par nombre de votes (numVotes) dans l'ordre décroissant
        films_tries = films_filtrés.sort_values(by='numVotes', ascending=False)

        # Sélectionner les 6 films avec le plus de votes
        films_choisis = films_tries.head(6)

        # Ajouter un style CSS pour centrer le texte et limiter la hauteur des titres
        st.markdown("""
            <style>
            .center-text {
                text-align: center;
                height: 2em;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
            .film-poster {
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            </style>
        """, unsafe_allow_html=True)

        # Afficher la liste des films
        cols = st.columns(6)
        for i, (index, film) in enumerate(films_choisis.iterrows()):
            film_details = get_film_details(film['tconst'], api_key)
            if film_details:
                poster_path = film_details.get('poster_path')
                if poster_path:
                    poster_url = IMAGE_BASE_URL + poster_path
                    col = cols[i % len(cols)]
                    with col:
                            st.write(f'<p class="center-text">{film["title"]}</p>', unsafe_allow_html=True)
                            st.image(poster_url, caption="", width=230)
                            if st.button("", key=f"button_{index}"):
                                st.session_state.selected_film = film['tconst']
                                st.experimental_rerun()

    



############################################################################################################# Onglet 'Year'
with tab_year:
    # Afficher les détails du film si un film est sélectionné
    if 'selected_film' in st.session_state and st.session_state.selected_film is not None:
        # Obtenir les détails du film sélectionné depuis l'API TMDb
        film_details = get_film_details(st.session_state.selected_film, api_key)

        if film_details:
            # Récupérer les informations du film
            film_title = film_details.get('title')
            poster_path = film_details.get('poster_path')
            overview = film_details.get('overview', "Synopsis non disponible")
            release_date = film_details.get('release_date')
            vote_average = film_details.get('vote_average')

            # Arrondir vote_average à un chiffre après la virgule 
            if vote_average is not None:
                vote_average = round(vote_average, 1)

            # Extraire l'année à partir de la date de sortie
            release_year = release_date[:4] if release_date else "Année inconnue"

            genres_data = film_details.get('genres', [])
 
            # Extraire le nom de chaque genre
            genre_names = [genre.get('name', '') for genre in genres_data]

            # Joindre les noms des genres en une seule chaîne de caractères
            genres_string = ', '.join(genre_names)


            # URL complète de l'affiche du film
            if poster_path:
                poster_url = IMAGE_BASE_URL + poster_path

                # Afficher les détails du film
                col1, col2, col3, col4 = st.columns([3, 2, 4, 1])

                with col1:
                    st.image(poster_url, width=400)

                with col2:
                    # Affichage du titre du film
                    st.markdown(
                        f"""
                        <div style='text-align: center; margin-bottom: 80px;'>
                            <h2>{film_title}</h2>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    # Affichage des informations sur le film
                    st.markdown(
                        f"""
                        <div style='display: flex; justify-content: center; align-items: center; height: 100%; margin-bottom: 100px'>
                            <div style='text-align: center;'>
                                <p><strong style='color: #3ECDC5;'>Année de sortie :</strong> <span style='color: white;'>{release_year}</span></p>
                                <p><strong style='color: #3ECDC5;'>Note :</strong> <span style='color: white;'>{vote_average}</span></p>
                                <p><strong style='color: #3ECDC5;'>Genres :</strong> <span style='color: white;'>{genres_string}</span></p>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with col3:
                    # Affichage du synopsis du film
                    st.markdown(
                        f"""
                        <div style='display: flex; justify-content: center; align-items: center; height: 100%; margin-bottom: 100px'>
                            <div>
                                <h4>Synopsis :</h4>
                                <p>{overview}</p>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                # Bouton pour revenir à la sélection par année
                if st.button("Retour", key="back_button_year"):
                    del st.session_state.selected_film
                    st.experimental_rerun()
    else:
        # Afficher la sélection par année
        # Créez trois colonnes avec les largeurs différentes pour la taille du selectbox
        col1, col2, col3 = st.columns([1, 1, 7])

        # Placez la selectbox dans la 1ere colonne
        with col1:
            selected_year = st.selectbox("", year)

        # Filtrer les films selon l'année sélectionnée et les critères de vote et de note
        films_filtrés = df[(df['year'] == selected_year) & (df['numVotes'] > 100000)]

        # Trier les films filtrés par numvotes décroissant
        films_tries = films_filtrés.sort_values(by='numVotes', ascending=False)

        # Sélectionner les 6 films avec les meilleures notes
        films_choisis = films_tries.head(6)

        # Ajouter un style CSS pour centrer le texte et limiter la hauteur des titres
        st.markdown("""
            <style>
            .center-text {
                text-align: center;
                height: 2em;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
            .film-poster {
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            </style>
        """, unsafe_allow_html=True)

        # Afficher les films choisis dans les colonnes
        cols = st.columns(6)
        for i, (index, film) in enumerate(films_choisis.iterrows()):
            # Obtenir les détails du film depuis l'API TMDb
            film_details = get_film_details(film['tconst'], api_key)

            if film_details:
                # Récupérer l'URL complète de l'affiche du film
                poster_path = film_details.get('poster_path')

                if poster_path:
                    # Construire l'URL complète de l'affiche du film
                    poster_url = IMAGE_BASE_URL + poster_path

                    # Afficher l'affiche du film dans la colonne appropriée
                    col = cols[i % len(cols)]
                    with col:
                        # Ajouter la classe pour centrer le texte
                        st.write(f'<p class="center-text">{film["title"]}</p>', unsafe_allow_html=True)
                        st.image(poster_url, caption="", width=230)
                        # Afficher l'affiche du film
                        if st.button("", key=f"button_{film['tconst']}"):
                            st.session_state.selected_film = film['tconst']
                            st.experimental_rerun()
                        

#################################################################################################### Onglet 'Search Movie'
with tab_search_movie:
    # Boîte de texte de recherche
    title_input = st.text_input("Entrez le titre d'un film")

    # Si l'utilisateur a entré un titre de film
    if title_input:
        # Trouver les films les plus proches en utilisant le titre saisi
        closest_films = find_closest_films_by_title(title_input, data_normalized, knn, df)

        if not closest_films.empty:
            # Si aucun film n'est sélectionné, afficher la phrase 
            if st.session_state.selected_film is None:
                st.subheader("Vous pourriez aimer :")



# Si un film est sélectionné, afficher ses détails
            if st.session_state.selected_film is not None:
                film = closest_films.loc[st.session_state.selected_film]

                # Obtenir les détails du film depuis l'API TMDb
                film_details = get_film_details(film['tconst'], api_key)

                if film_details:
                    poster_path = film_details.get('poster_path')
                    overview = film_details.get('overview', "Synopsis non disponible")
                    if poster_path:
                        poster_url = IMAGE_BASE_URL + poster_path
                        col1, col2, col3, col4 = st.columns([2, 2, 4, 1])  # colonnes avec largeurs relatives
                        
                       
                        with col1:
                            st.image(poster_url, width=340)
                        with col2:
                            # Affichage du titre du film
                            st.markdown(
                                f"""
                                <div style='text-align: center; margin-bottom: 80px;'>
                                    <h2>{film['title']}</h2>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                            # Affichage des informations sur le film
                            st.markdown(
                                f"""
                                <div style='display: flex; justify-content: center; align-items: center; height: 100%; margin-bottom: 100px'>
                                    <div style='text-align: center;'>
                                        <p><strong style='color: #3ECDC5;'>Année de sortie :</strong> <span style='color: white;'>{film['year']}</span></p>
                                        <p><strong style='color: #3ECDC5;'>Note :</strong> <span style='color: white;'>{film['averageRating']}</span></p>
                                        <p><strong style='color: #3ECDC5;'>Votes :</strong> <span style='color: white;'>{film['numVotes']}</span></p>
                                        <p><strong style='color: #3ECDC5;'>Genres :</strong> <span style='color: white;'>{', '.join(genre for genre, value in film[genres_available].items() if value == 1)}</span></p>
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                        with col3:
                            st.markdown(
                                f"""
                                <div style='display: flex; justify-content: center; align-items: center; height: 100%; margin-bottom: 100px'>
                                    <div>
                                        <h4>Synopsis :</h4>
                                        <p>{overview}</p>
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            if film_details:
                                # Obtenir les informations sur les acteurs
                                cast = film_details.get('credits', {}).get('cast', [])

                                # Afficher les photos des trois premiers acteurs dans les colonnes 2, 3 et 4
                                for i, actor in enumerate(cast[:3]):
                                    profile_path = actor.get('profile_path')
                                    if profile_path:
                                        actor_name = actor.get('name')
                                        actor_image_url = f"https://image.tmdb.org/t/p/w185{profile_path}"
                                        col = cols[i]                                                        # Commencez à partir de la deuxième colonne
                                        with col:
                                            st.markdown(f"**{actor_name}**")
                                            st.image(actor_image_url, caption=actor_name, use_column_width=True)

                    if st.button("Retour", key="back_button"):
                        st.session_state.selected_film = None
                        st.experimental_rerun()

            # Sinon, afficher la liste des films
            else:
                # CSS pour centrer le texte et limiter la hauteur des titres
                st.markdown("""
                    <style>
                    .film-title {
                        text-align: center;
                        height: 3em;
                        overflow: hidden;
                        text-overflow: ellipsis;
                        white-space: nowrap;
                    }
                    </style>
                """, unsafe_allow_html=True)

                 # Initialiser les colonnes pour afficher les affiches des films
                cols = st.columns(6)

                # Parcourir les films recommandés et les afficher dans les colonnes
                for i, (_, film) in enumerate(closest_films.iterrows()):
                    # Obtenir les détails du film depuis l'API TMDb
                    film_details = get_film_details(film['tconst'], api_key)

                    if film_details:
                        poster_path = film_details.get('poster_path')

                        if poster_path:
                            poster_url = IMAGE_BASE_URL + poster_path
                            col = cols[i % len(cols)]
                            with col:
                                st.markdown(f"<h3 class='film-title'>{film['title']}</h3>", unsafe_allow_html=True)
                                # Utilisez la classe "no-scale" et "img-hover" pour les images
                                st.markdown(
                                    f'<img src="{poster_url}" class="no-scale" width="230">',
                                    unsafe_allow_html=True
                                )
                                if st.button("", key=f"poster_button_{i}"):
                                    st.session_state.selected_film = film.name
                                    st.experimental_rerun()

                                


                           
