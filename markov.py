import requests
import sys
import os
import hashlib
from pymarkovchain import MarkovChain
import glob
import re

def parse_file(text):
    main_artist = text.split('\n', 1)[0]    #first line contains main artist
    unparsed_lyrics = text.split('\n', 1)[1]

    #split into verses
    verses = unparsed_lyrics.split('[')
    #print(verses)
    verses = verses[1:]     #drop the first string cause its empty

    combined_verses = ""
    for i, verse in enumerate(verses):
        #parse verse artist
        verse_artists = []
        tag = verse.split(']',1)[0]
        # print(tag)

        # Parse verse lyrics
        verse_lyrics = verse.split(']',1)[1]
        print(i, verse_lyrics)

        verse_lyrics
        combined_verses += verse_lyrics+"\n"

    return combined_verses



lyrics_directory = "data1/"
files = glob.glob(lyrics_directory+'*.txt')
# iterate over the list getting each file
all_lyrics = ""
for file in files:
    # open the file and then call .read() to get the text
    print(file)
    with open(file) as f:
        text = f.read()
        verse_lyrics = parse_file(text)
        verse_lyrics = re.sub("[\[\]\(\)\"]", " ", verse_lyrics)
        verse_lyrics = re.sub(" +", " ", verse_lyrics)
        all_lyrics += verse_lyrics
    

mc = MarkovChain("test")
mc.generateDatabase(all_lyrics)

output_directory = "generated_lyrics/"
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

number_of_phrases = 8
num_files = 1000
for i in range(num_files):
    # Printing a string
    with open(output_directory+"{}.txt".format(i), "w") as f:
        for i in range(0, int(number_of_phrases)):
            
            while True:
                line = mc.generateString()
                if len(line) > 1:
                    break

            print(line)
            f.write(line+"\n")
    print("")


