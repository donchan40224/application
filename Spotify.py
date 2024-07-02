import streamlit as st
from requests import post, get
import json
import base64
import pandas as pd
import csv
import io

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
    query = f'?q=track:{track_name.strip()}%20artist:{artist_name.strip()}&type=track'
    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)
    return json_result

def get_features(token, tracks_id):
    headers = get_auth_header(token)
    url = f"https://api.spotify.com/v1/audio-features?ids={tracks_id}"
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    return json_result

def app():
    st.title("Spotify Track Information")

    # Get user input
    track_name = st.text_input("Enter the track name").strip()
    artist_name = st.text_input("Enter the artist name").strip()

    if st.button("Get Track Information"):
        # Get the track information
        token = get_token()
        track_info_json = get_track_info(token, track_name, artist_name)

        # Process the track information and create the data frame
        columns = ["track_name", "track_popularity", "duration_ms", "artist_name", "feats", "album", "type", "release_date", "track_id", "artist_id"]
        df_playlist = pd.DataFrame(columns=columns)

        track_info = track_info_json["tracks"]["items"]
        feats = []

        for i in range(len(track_info)):
            data = {
                "track_name": track_info[i]["name"],
                "track_popularity": track_info[i]["popularity"],
                "artist_name": track_info[i]["artists"][0]["name"],
                "duration_ms": track_info[i]["duration_ms"],
                "feats": "",
                "album": track_info[i]["album"]["name"],
                "type": track_info[i]["album"]["album_type"],
                "release_date": track_info[i]["album"]["release_date"],
                "track_id": track_info[i]["id"],
                "artist_id": track_info[i]["artists"][0]["id"]
            }

            if len(track_info[i]["artists"]) > 1:
                for j in range(len(track_info[i]["artists"]) - 1):
                    feats.append(track_info[i]["artists"][j + 1]["name"])
                data["feats"] = "|".join(feats)
            else:
                data["feats"] = None
            feats = []

            df_playlist = pd.concat([df_playlist, pd.DataFrame([data])], ignore_index=True)

        # Add additional features to the data frame
        tracks_id = list(df_playlist["track_id"])
        tracks_id = ",".join(tracks_id)
        df_features = get_features(token, tracks_id)["audio_features"]
        df_features = pd.DataFrame(df_features)
        df_features = df_features[["acousticness", "danceability", "energy", "instrumentalness", "liveness", "loudness", "valence", "mode", "tempo", "id"]]
        result_df = pd.merge(df_playlist, df_features, left_on='track_id', right_on='id')
        result_df = result_df.drop('id', axis=1)

        # Display the data frame
        st.write(result_df)

        # Download CSV button
        csv_data = result_df.to_csv(index=False, encoding='utf-8')
        b64 = base64.b64encode(csv_data.encode()).decode()
        file_name = f"{artist_name}_{track_name}.csv"
        href = f'<a href="data:file/csv;base64,{b64}" download="{file_name}">Download CSV</a>'
        st.markdown(href, unsafe_allow_html=True)

if __name__ == "__main__":
    app()
