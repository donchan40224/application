import streamlit as st
from requests import post, get
import json
import base64
import pandas as pd

CLIENT_ID = '46bef0c0bbf74f05b2ab82e420cafd34'
CLIENT_SECRET = 'c775d3a026614d42953279c45ab5d711'

def get_token():
    auth_string = CLIENT_ID + ":" + CLIENT_SECRET
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"

    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result
    return token["access_token"]

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def get_track_info(token, track_name, artist_name):
    headers = get_auth_header(token)
    url = 'https://api.spotify.com/v1/search'
    query = f'?q=track:{track_name}%20artist:{artist_name}&type=track'
    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)
    return json_result

def get_artist(token,artist_id):
    url=f"https://api.spotify.com/v1/artists/{artist_id}"
    headers = get_auth_header(token)
    result = get(url,headers=headers)
    json_result = json.loads(result.content)
    return json_result

def get_features(token,songs_id):
    url=f"https://api.spotify.com/v1/audio-features?ids={songs_id}"
    headers = get_auth_header(token)
    result = get(url,headers=headers)
    json_result = json.loads(result.content)
    return json_result

def app():
    st.title("Spotify Track Information")

    # Get user input
    track_name = st.text_input("Enter the track name")
    artist_name = st.text_input("Enter the artist name")

    if st.button("Get Track Information"):
        # Get the track information
        token = get_token()
        track_info_json = get_track_info(token, track_name, artist_name)

        # Process the track information and create the data frame
        columns = ["top", "track_name", "track_popularity", "duration_ms", "artist_name", "artist_genres", "artist_popularity", "feats", "explicit", "album", "type", "release_date", "track_id", "artist_id"]
        df_playlist = pd.DataFrame(columns=columns)

        track_info = track_info_json["tracks"]["items"]
        feats = []

        for i in range(len(track_info)):
            data = {
                "top": i + 1,
                "track_name": track_info[i]["name"],
                "track_popularity": track_info[i]["popularity"],
                "artist_name": track_info[i]["artists"][0]["name"],
                "artist_genres": "",
                "duration_ms": track_info[i]["duration_ms"],
                "artist_popularity": "",
                "feats": "",
                "explicit": track_info[i]["explicit"],
                "album": track_info[i]["album"]["name"],
                "type": track_info[i]["album"]["album_type"],
                "release_date": track_info[i]["album"]["release_date"],
                "track_id": track_info[i]["id"],
                "artist_id": track_info[i]["artists"][0]["id"]
            }

            artist_info = get_artist(token, data["artist_id"])
            data["artist_popularity"] = artist_info["popularity"]

            if len(artist_info["genres"]) == 1:
                data["artist_genres"] = artist_info["genres"][0]
            elif len(artist_info["genres"]) > 1:
                genres = artist_info["genres"]
                data["artist_genres"] = "|".join(genres)
            else:
                data["artist_genres"] = None

            if len(track_info[i]["artists"]) > 1:
                for j in range(len(track_info[i]["artists"]) - 1):
                    feats.append(track_info[i]["artists"][j + 1]["name"])
                data["feats"] = "|".join(feats)
            else:
                data["feats"] = None
            feats = []

            df_playlist = pd.concat([df_playlist, pd.DataFrame([data])], ignore_index=True)

        # Display the data frame
        st.write(df_playlist)

if __name__ == "__main__":
    app()
