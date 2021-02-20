import requests
from bs4 import BeautifulSoup
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--output_filename', type=str, default="artists.txt", help='name of the output file containing rappers instagrams')
args = parser.parse_args()

# Constants
API_BASE_URL = "https://genius.com/api"
CHART_BASE_URL = API_BASE_URL + '/songs/chart?'
NUM_SONGS_PER_PAGE = 50


def parse_featured_artists_song_page(json_response):
    featured_artists = json_response["response"]["song"]["featured_artists"]
    featured_artists_ids = [a["id"] for a in featured_artists]
    return featured_artists_ids

def parse_charts_page(json_response, include_featured_artists = True):
    """
    Parse songs chart page and returns a list of ids of the main artist or artists featured on the songs
    """
    chart_songs = json_response["response"]["chart_items"]

    artist_ids = []
    for song in chart_songs:
        song_url = API_BASE_URL + song["item"]["api_path"]
        artist_id = song["item"]["primary_artist"]["id"]
        artist_ids.append(artist_id)

        if include_featured_artists:
            response = requests.get(song_url)
            song_json_response = response.json()
            if response.status_code == 200:
                featured_artists_ids = parse_featured_artists_song_page(song_json_response)
                artist_ids.extend(featured_artists_ids)
    return artist_ids


# Get list of top songs and their api path
print("Searching RapGenius charts for Rap Artists...")

artists_urls = []   # list of artists rapgenius pages
for time_period in ["all_time", "month", "week", "day"]:
    print("Searching {} charts...".format(time_period))

    current_page = 1
    while True:
        # Get charts page
        current_url = CHART_BASE_URL + 'page=' + str(current_page) + '&per_page=' + str(NUM_SONGS_PER_PAGE) + '&time_period='+ time_period +'&chart_genre=rap'

        response = requests.get(current_url)
        json_response = response.json()

        artist_ids = parse_charts_page(json_response, True)

        if len(artist_ids) == 0:
            break

        for artist_id in artist_ids:
            artist_url = "/artists/"+str(artist_id)

            if artist_url not in artists_urls:
                artists_urls.append(artist_url)

        current_page += 1
print("Search in charts completed.")

# Find the instagram name of each artist
print("Finding instagram names...")
instagram_handles = []
for artist_url in artists_urls:
    current_url = API_BASE_URL + artist_url

    response = requests.get(current_url)
    json_response = response.json()

    artist_name = json_response["response"]["artist"]["name"]
    handle = json_response["response"]["artist"]["instagram_name"]

    if handle is not None and handle != "":
        if handle not in instagram_handles:
            print("{}: {}".format(artist_name, handle))

            instagram_handles.append(handle)
    else:
        print("{}: Not found".format(artist_name))

print("Found {}/{} instagram names.".format(len(instagram_handles), len(artists_urls)))

with open(args.output_filename, "w") as f:
    f.write("\n".join(instagram_handles))

print("Instagram names saved to {}".format(args.output_filename))