import requests


def get_book_metadata(title: str):
    response = requests.get("https://openlibrary.org/search.json", params={"title": title})
    data = response.json()
    docs = data["docs"]
    if not docs:
        return None
    first_result = docs[0]
    key, cover_key, year = first_result.get("key"), first_result.get("cover_edition_key"), first_result.get("first_publish_year")
    cover = f"https://covers.openlibrary.org/b/olid/{cover_key}-M.jpg" if cover_key else None

    return {
        "external_id": key,
        "cover_image": cover,
        "release_year": year
    }

def get_movie_metadata(title: str):
    # response = requests.get("https://image.tmdb.org/search.json", params={"title": title})
    # data = response.json()
    # docs = data["docs"]
    # if not docs:
    #     return None
    # first_result = docs[0]
    # key, poster_path, year = first_result.get("id"), first_result.get("poster_path"), first_result.get("release_date")
    # poster = f"https://image.tmdb.org/t/p/w500{poster_path}"

    # return {
    #     "external_id": key,
    #     "cover_image": poster,
    #     "release_year": year
    # }
    return None


def get_tv_metadata(title: str):
    return None


def get_game_metadata(title: str):
    return None