from requests import post,get
import json
import base64
import pandas as pd


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

def get_track_info(token, track_name, artist_name):
    headers = get_auth_header(token)
    url = 'https://api.spotify.com/v1/search'
    query = f'?q=track:{track_name}%20artist:{artist_name}&type=track'
    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)
    return json_result

def app():
    st.title("Spotify Track Information")

    # Get user input
    track_name = st.text_input("Enter the track name")
    artist_name = st.text_input("Enter the artist name")

    if st.button("Get Track Information"):
        # Get the token
        token = get_token()

        # Get the track information
        result = get_track_info(token, track_name, artist_name)

        # Extract the track information
        track_data = []
        try:
            for item in result["tracks"]["items"]:
                track_info = {
                    "track_popularity": item["popularity"],
                    "duration_ms": item["duration_ms"],
                    "artist_name": ", ".join([artist["name"] for artist in item["artists"]]),
                    "artist_genres": ", ".join(item["artists"][0]["genres"]),
                    "artist_popularity": item["artists"][0]["popularity"],
                    "feats": ", ".join([artist["name"] for artist in item["artists"][1:]]),
                    "explicit": item["explicit"],
                    "album": item["album"]["name"],
                    "type": item["type"],
                    "release_date": item["album"]["release_date"],
                    "track_id": item["id"]
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
