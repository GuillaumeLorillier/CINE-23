import requests
import pandas as pd
from st_clickable_images import clickable_images  # Importez la fonction clickable_images

# Fonction pour récupérer les détails d'un film à partir de l'API TMDb
def get_film_details(tconst, api_key, language='fr'):
    url = f"https://api.themoviedb.org/3/movie/{tconst}"
    params = {"api_key": api_key, "language": language, "append_to_response": "videos"}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    
# Fonction pour obtenir les images du film depuis l'API TMDb
def get_film_images(tconst, api_key, language='fr'):
    url = f"https://api.themoviedb.org/3/movie/{tconst}/images"
    params = {
        "api_key": api_key,
        "language": language
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        # Retourne les images du film (backdrops)
        return data.get('backdrops', [])
    else:
        return []

# Fonction pour rendre les images cliquables et retourner l'index de l'image cliquée
def render_clickable_images(paths, titles):
    return clickable_images(
        paths=paths,
        titles=titles,
        div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap"},
        img_style={"margin": "5px", "height": "200px"},
        key="genre_images"
    )

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

# Fonction pour récupérer l'URL de la bande-annonce d'un film à partir de la réponse JSON des détails du film
def get_trailer_url(film_details):
    if "videos" in film_details:
        videos = film_details["videos"]["results"]
        for video in videos:
            # Recherche de la bande-annonce officielle
            if video["type"] == "Trailer" and video["site"] == "YouTube":
                return f"https://www.youtube.com/watch?v={video['key']}"
    return None
