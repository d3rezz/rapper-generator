import requests
from bs4 import BeautifulSoup
import re
import os
import math

genius_base_url = 'http://genius.com'
api_base_url = "https://genius.com/api"
chart_base_url = api_base_url+ '/songs/chart?'

num_songs_per_page = 50
num_songs = 10
num_pages = math.ceil(num_songs/num_songs_per_page)



top_songs_api_path = []

lyrics_directory = "./lyrics/"
directory = os.path.dirname(lyrics_directory)
if not os.path.exists(directory):
    os.makedirs(directory)

print('Rap Genius Top Songs Scraper')

#Scrape top songs api path
for page in range(1,num_pages+1):
    current_url = chart_base_url + 'page=' + str(page) + '&per_page=' + str(num_songs_per_page) + '&time_period=all_time&tag_id=1434'
    print(current_url)

    response = requests.get(current_url)

    json = response.json()

    num_songs_returned = len(json["response"]["chart_items"])
    if num_songs_returned == 0:
        break

    for song in range(num_songs_returned):
        song_api_path = json["response"]["chart_items"][song]["item"]["api_path"]

        print(song_api_path)
        top_songs_api_path.append(song_api_path)


if len(top_songs_api_path) > num_songs:
    top_songs_api_path = top_songs_api_path[:num_songs]

print("Collected api path of "+str(len(top_songs_api_path))+" songs")


#Fetch lyrics for each song in top_songs_api_path list
song_num = 1
for song_path in top_songs_api_path:
    print("Progress: "+str(song_num)+"/"+str(len(top_songs_api_path)))
    response = requests.get(api_base_url+song_path)
    json = response.json()
    path = json["response"]["song"]["path"]

    tracking_data = json["response"]["song"]["tracking_data"]
    print(tracking_data)

    #regular scraping on rap genius website
    page_url = genius_base_url + path

    page = requests.get(page_url)
    html = BeautifulSoup(page.text, "html.parser")
    #remove script tags
    [h.extract() for h in html('script')]

    lyrics = html.find('div', class_='lyrics').get_text()
    #print(lyrics)

    #Remove everything until first artist tag
    pos = lyrics.find("[")
    lyrics = lyrics[pos:]
    #print(lyrics)

    #Remove white space
    lyrics = "\n".join([ll.rstrip() for ll in lyrics.splitlines() if ll.strip()])

    #Remove produced by line
    lyrics = re.sub(".*produced by.*\n?","",lyrics, flags=re.IGNORECASE)

    #add artist on first line
    main_artist = html.find_all("a", "header_with_cover_art-primary_info-primary_artist")[0].string
    lyrics = main_artist+'\n'+lyrics

    #write to file
    text_file = open(lyrics_directory+str(song_num)+".txt", "w")
    text_file.write(lyrics)
    text_file.close()

    song_num += 1
