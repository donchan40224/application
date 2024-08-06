import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import time

# Streamlit app title
st.title('Spotify Track Information Retriever')

# Input fields
track_name = st.text_input('Enter Track Name (optional)')
artist_name = st.text_input('Enter Artist Name (optional)')
max_results = st.number_input('Maximum Number of Results', min_value=1, max_value=1000, value=100)
exact_match = st.checkbox('Exact Match')

# Spotify API credentials
client_id = st.secrets["46bef0c0bbf74f05b2ab82e420cafd34"]
client_secret = st.secrets["c775d3a026614d42953279c45ab5d711"]

def get_spotify_info(track_name=None, artist_name=None, max_results=1000, exact_match=False):
    # Set up Spotify API credentials
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    
    # Perform search based on provided parameters
    query = ''
    if track_name:
        query += f'track:"{track_name}"' if exact_match else f'track:{track_name}'
        query += ' '
    if artist_name:
        query += f'artist:"{artist_name}"' if exact_match else f'artist:{artist_name}'
    
    if not query:
        st.error("At least one of track name or artist name must be provided")
        return pd.DataFrame()
    
    results = []
    offset = 0
    limit = 50  # Maximum allowed by Spotify API per request

    progress_bar = st.progress(0)
    status_text = st.empty()

    while len(results) < max_results:
        try:
            response = sp.search(q=query, type='track', limit=limit, offset=offset)
            if not response['tracks']['items']:
                break
            results.extend(response['tracks']['items'])
            offset += limit
            if offset >= 1000:  # Spotify API doesn't allow offset > 1000
                break
            progress = min(len(results) / max_results, 1.0)
            progress_bar.progress(progress)
            status_text.text(f"Fetched {len(results)} tracks...")
            time.sleep(0.1)  # Add a small delay to avoid hitting rate limits
        except spotipy.SpotifyException as e:
            st.error(f"Error occurred: {e}")
            break

    st.info(f"Total tracks found: {len(results)}")

    if not results:
        return pd.DataFrame()  # Return empty DataFrame if no results found

    track_info_list = []
    
    for i, track in enumerate(results[:max_results]):
        # Extract basic track information
        track_info = {
            'track_name': track['name'],
            'artist_name': track['artists'][0]['name'],
            'album': track['album']['name'],
            'release_date': track['album']['release_date'],
            'popularity': track['popularity'],
        }
        
        # Get artist information
        try:
            artist = sp.artist(track['artists'][0]['id'])
            track_info.update({
                'artist_popularity': artist['popularity'],
                'genres': ', '.join(artist['genres'])
            })
        except spotipy.SpotifyException as e:
            st.warning(f"Error getting artist info: {e}")
        
        # Get audio features
        try:
            audio_features = sp.audio_features(track['id'])[0]
            if audio_features:
                track_info.update({
                    'danceability': audio_features['danceability'],
                    'energy': audio_features['energy'],
                    'key': audio_features['key'],
                    'loudness': audio_features['loudness'],
                    'mode': audio_features['mode'],
                    'speechiness': audio_features['speechiness'],
                    'acousticness': audio_features['acousticness'],
                    'instrumentalness': audio_features['instrumentalness'],
                    'liveness': audio_features['liveness'],
                    'valence': audio_features['valence'],
                    'tempo': audio_features['tempo'],
                    'duration_ms': audio_features['duration_ms'],
                    'time_signature': audio_features['time_signature']
                })
        except spotipy.SpotifyException as e:
            st.warning(f"Error getting audio features: {e}")
        
        track_info_list.append(track_info)
        
        progress = (i + 1) / min(len(results), max_results)
        progress_bar.progress(progress)
        status_text.text(f"Processed {i + 1} tracks...")
        
        time.sleep(0.1)  # Add a small delay to avoid hitting rate limits
    
    # Create DataFrame
    df = pd.DataFrame(track_info_list)
    
    st.success(f"Final number of tracks in DataFrame: {len(df)}")
    
    return df

# Button to trigger the search
if st.button('Search'):
    if track_name or artist_name:
        df = get_spotify_info(track_name, artist_name, max_results, exact_match)
        if not df.empty:
            st.dataframe(df)
        else:
            st.warning("No results found.")
    else:
        st.error("Please enter at least a track name or an artist name.")

# Instructions
st.markdown("""
## How to use:
1. Enter a track name, artist name, or both.
2. Specify the maximum number of results you want (up to 1000).
3. Check 'Exact Match' if you want an exact match for the track or artist name.
4. Click 'Search' to retrieve the information.


## Audio Features Explanation:
- Danceability: How suitable a track is for dancing (0.0 to 1.0)
- Energy: Perceptual measure of intensity and activity (0.0 to 1.0)
- Key: The key the track is in (0 = C, 1 = C♯/D♭, 2 = D, and so on)
- Loudness: Overall loudness of a track in decibels (dB)
- Mode: Modality of a track (0 for minor, 1 for major)
- Speechiness: Presence of spoken words in a track (0.0 to 1.0)
- Acousticness: Confidence measure of whether the track is acoustic (0.0 to 1.0)
- Instrumentalness: Predicts whether a track contains no vocals (0.0 to 1.0)
- Liveness: Detects the presence of an audience in the recording (0.0 to 1.0)
- Valence: Musical positiveness conveyed by a track (0.0 to 1.0)
- Tempo: Overall estimated tempo of a track in beats per minute (BPM)
- Duration_ms: The duration of the track in milliseconds
- Time_signature: An estimated time signature
""")
