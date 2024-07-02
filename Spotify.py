from requests import post,get
import json
import base64


CLIENT_ID = '46bef0c0bbf74f05b2ab82e420cafd34'
CLIENT_SECRET = 'c775d3a026614d42953279c45ab5d711'
def get_token():
    auth_string = CLIENT_ID+":"+CLIENT_SECRET 
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"

    headers = {
        "Authorization" : "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {"grant_type":"client_credentials"}
    result = post(url,headers=headers,data=data)
    json_result = json.loads(result.content)
    token = json_result
    return token["access_token"]

def get_auth_header(token):
    return {"Authorization": "Bearer "+ token}

def get_id(token, track_name, artist_name):
    headers = get_auth_header(token)
    url = 'https://api.spotify.com/v1/search'
    query = f'?q=track:{track_name}%20artist:{artist_name}&type=track'
    query_url = url+query
    result = get(query_url,headers=headers)
    json_result = json.loads(result.content)
    print(json_result)  # Add this line to print the API response
    return json_result

import streamlit as st
import pandas as pd

def app():
    st.title("Spotify Track Information")

    track_name = st.text_input("Enter the track name")
    artist_name = st.text_input("Enter the artist name")

    if track_name and artist_name:
        token = get_token()
        result = get_id(token, track_name, artist_name)

        track_data = []
        try:
            for item in result["tracks"]["items"]:
                track_info = {
                    "track_name": item["track"]["name"],
                    "track_popularity": item["track"]["popularity"],
                    "duration_ms": item["track"]["duration_ms"],
                    "artist_name": item["track"]["artists"][0]["name"],
                    "artist_popularity": item["artists"][0]["popularity"],
                    "explicit": item["track"]["explicit"],
                    "album": item["track"]["album"]["name"],
                    "type": item["track"]["album"]["album_type"],
                    "release_date": item["track"]["album"]["release_date"],
                    "track_id": item["track"]["id"]
                }
                track_data.append(track_info)
        except (KeyError, TypeError):
            st.write("No tracks found.")

        # Display the track information in a data frame
        if track_data:
            df = pd.DataFrame(track_data)
            st.write(df)
        else:
            st.write("No tracks found.")

if __name__ == "__main__":
    app()
