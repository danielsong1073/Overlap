import requests
import os
from dotenv import load_dotenv

load_dotenv()

apikey = os.getenv("OMDB_API_KEY")
rawgkey = os.getenv("RAWG_API_KEY")


def get_book_metadata(title: str):
    response = requests.get("https://openlibrary.org/search.json", params={"title": title})
    data = response.json()
    docs = data["docs"]
    if not docs:
        return None
    first_result = docs[0]
    work_id, cover_key, year = first_result.get("key"), first_result.get("cover_edition_key"), first_result.get("first_publish_year")
    cover = f"https://covers.openlibrary.org/b/olid/{cover_key}-M.jpg" if cover_key else None

    return {
        "external_id": work_id,
        "cover_image": cover,
        "release_year": year
    }

def get_movie_metadata(title: str):
    response = requests.get("https://www.omdbapi.com/", params={"t": title, "apikey": apikey})
    data = response.json()
    if data.get("Response") == "False":
        return None
    imdb_id, poster, date = data.get("imdbID"), data.get("Poster"), data.get("Released")
    year = int(date[-4:]) if date else None

    return {
        "external_id": imdb_id,
        "cover_image": poster,
        "release_year": year
    }


def get_tv_metadata(title: str):
    response = requests.get("https://www.omdbapi.com/", params={"t": title, "apikey": apikey, "type": "series"})
    data = response.json()
    if data.get("Response") == "False":
        return None
    imdb_id, poster, date = data.get("imdbID"), data.get("Poster"), data.get("Released")
    year = int(date[-4:]) if date else None

    return {
        "external_id": imdb_id,
        "cover_image": poster,
        "release_year": year
    }


def get_game_metadata(title: str):
    response = requests.get("https://api.rawg.io/api/games", params={"search": title, "key": rawgkey})
    data = response.json()
    results = data["results"]
    if not results:
        return None
    first_result = results[0]
    game_id, image, released = first_result.get("id"), first_result.get("background_image"), first_result.get("released")
    year = int(released[:4]) if released else None

    return {
        "external_id": game_id,
        "cover_image": image,
        "release_year": year
    }