import urllib.parse, urllib.request, urllib.error, json
#from bs4 import BeautifulSoup


def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)


# q_track=Ball%20for%20me&q_artist=post%20malone&apikey=8f059b33da893bff6d6891ffee7a9902



def getLyrics(trackname, artist, apikey="8f059b33da893bff6d6891ffee7a9902"):
    base_url = "https://api.musixmatch.com/ws/1.1/matcher.lyrics.get?format=json&callback=callback&"
    new_dict = {"q_track": trackname, "q_artist": artist, "apikey": apikey}
    query_params = urllib.parse.urlencode(new_dict)
    url = base_url + query_params
    resp = urllib.request.urlopen(url)
    requeststr = resp.read()
    json_obj = json.loads(requeststr)
    lyrics = json_obj['message']['body']['lyrics']['lyrics_body']
    list = [json_obj['message']['body']['lyrics']['lyrics_id'], lyrics]

    return list[1]


lyrics = getLyrics("Ball for me", "Post malone")
print(lyrics)


import paralleldots
paralleldots.set_api_key( "LuNWzJKxQORA6RYOej5pEcaGNhqTYVUqFuBiwD9Oc1w" )
print( "\nEmotion" )
r = paralleldots.emotion(lyrics)
# r1 = paralleldots.sentiment(lyrics,"en")
#
# print(r)
# print(r1)

# import matplotlib.pyplot as plt
# import numpy as np
#
# emotions = r['emotion']
# print(emotions)
#
#
# label = emotions.keys()
# index = np.arange(len(label))
# no_movies = emotions.values()
#
# def plot_bar_x():
#     index = np.arange(len(label))
#     plt.bar(index, no_movies)
#     plt.xlabel('Emotion', fontsize=5)
#     plt.ylabel('Score', fontsize=5)
#     plt.xticks(index, label, fontsize=5, rotation=30)
#     plt.title('Emootions of the song')
#     plt.show()
#
# lol = plot_bar_x()
# lol
