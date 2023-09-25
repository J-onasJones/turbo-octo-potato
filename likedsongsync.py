import pylast, spotipy, sys, os, time
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# load .env file
load_dotenv()

# Define your Last.fm API credentials
LASTFM_API_KEY = os.getenv(' LASTFM_API_KEY')
LASTFM_API_SECRET = os.getenv('LASTFM_API_SECRET')
LASTFM_USERNAME = os.getenv('LASTFM_USERNAME')
LASTFM_PASSWORD_HASH = os.getenv('LASTFM_PASSWORD_HASH')

# Define your Spotify API credentials
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')

VERBOSE = True

def verboseprint(message):
    if VERBOSE:
        print(message)

#last.fm auth
def lastfmauth():
    SESSION_KEY_FILE = os.path.join(os.path.expanduser("~"), ".session_key")
    network = pylast.LastFMNetwork(LASTFM_API_KEY, LASTFM_API_SECRET)
    if not os.path.exists(SESSION_KEY_FILE):
        skg = pylast.SessionKeyGenerator(network)
        url = skg.get_web_auth_url()

        print(f"Please authorize this script to access your account: {url}\n")
        import time
        import webbrowser

        webbrowser.open(url)

        while True:
            try:
                session_key = skg.get_web_auth_session_key(url)
                with open(SESSION_KEY_FILE, "w") as f:
                    f.write(session_key)
                break
            except pylast.WSError:
                time.sleep(1)
    else:
        session_key = open(SESSION_KEY_FILE).read()

    network.session_key = session_key
    return network

#spotify
def spotifyauth():
    return spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                        client_secret=SPOTIPY_CLIENT_SECRET,
                                        redirect_uri=SPOTIPY_REDIRECT_URI,
                                        scope="user-library-read"))
def show_tracks(results):
    tracknr = results['offset']
    for item in results['items']:
        track = item['track']
        tracknr+=1
        verboseprint("%-10s %13s" % (f"ETA:{round((((int(results['total'])-tracknr)*0.25)/60))}min", f"[{tracknr}/{int(results['total'])}]") + "%32.32s %s" % (track['artists'][0]['name'], track['name']))
        #TODO: Fix this abomination
        try:
            track = network.get_track(track['artists'][0]['name'], track['name'])
            track.love()
        except pylast.NetworkError:
            try:
                time.sleep(1)
                track = network.get_track(track['artists'][0]['name'], track['name'])
                track.love()
            except pylast.NetworkError:
                verboseprint("Network error. Skipping..." + "%32.32s %s" % (track['artists'][0]['name'], track['name']))


verboseprint("Authenticating Spotify...")
sp = spotifyauth()
verboseprint("Done\nAuthenticating Last.fm")
network = lastfmauth()
verboseprint("Done!\nStarting...")

results = sp.current_user_saved_tracks()
show_tracks(results)

while results['next']:
    results = sp.next(results)
    show_tracks(results)
