import base64
from requests import post,get
import json


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
    return json_result

import streamlit as st

def app():
    st.title("Spotify Track ID Finder")

    # Get user input
    track_name = st.text_input("Enter the track name")
    artist_name = st.text_input("Enter the artist name")

    # Check if both inputs are provided
    if track_name and artist_name:
        # Get the token
        token = get_token()

        # Get the track ID(s)
        result = get_id(token, track_name, artist_name)

        # Display the result
        st.write(result)

if __name__ == "__main__":
    app()
