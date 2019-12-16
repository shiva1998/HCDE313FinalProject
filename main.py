import urllib
#import paralleldots
#import matplotlib.pyplot as plt
#import numpy as np
import webapp2, os, urllib2, json, jinja2, logging

import flickr_key as flickr_key



JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
                                       extensions=['jinja2.ext.autoescape'],
                                       autoescape=True)

def safeGet(url):
    try:
        return urllib2.urlopen(url)
    except urllib2.URLError as e:
        if hasattr(e, "code"):
            logging.error("The server couldn't fulfill the request.")
            logging.error("Error code: ", e.code)
        elif hasattr(e, 'reason'):
            logging.error("We failed to reach a server")
            logging.error("Reason: ", e.reason)
        return None

def getLyrics(trackname, artist, apikey="8f059b33da893bff6d6891ffee7a9902"):
    base_url = "https://api.musixmatch.com/ws/1.1/matcher.lyrics.get?format=json&callback=callback&"
    new_dict = {"q_track": trackname, "q_artist": artist, "apikey": apikey}
    query_params = urllib.urlencode(new_dict)
    url = base_url + query_params
    resp = safeGet(url)
    requeststr = resp.read()
    json_obj = json.loads(requeststr)
    lyrics = json_obj['message']['body']['lyrics']['lyrics_body']
    list = [json_obj['message']['body']['lyrics']['lyrics_id'], lyrics]

    return list[1]


def flickrREST(baseurl='https://api.flickr.com/services/rest',
               method='flickr.photos.search',
               api_key=flickr_key.key,
               format='json',
               params={},
               printurl=False
               ):
    params['method'] = method
    params['api_key'] = api_key
    params['format'] = format
    if format == "json":
        params['nojsoncallback'] = True
    url = baseurl + "?" + urllib.urlencode(params)
    if printurl:
        logging.info(url)
    return safeGet(url)


def getPhotoIDs(tags="Seattle", n=5):
    resp = flickrREST(params={"tags": tags, "per_page": n})
    if resp is not None:
        photosdict = json.loads(resp.read())['photos']
        if photosdict is not None:
            if 'photo' in photosdict and len(photosdict['photo']) > 0:
                return [photo['id'] for photo in photosdict['photo']]
    return None


def getPhotoInfo(photoID):
    resp = flickrREST(method="flickr.photos.getInfo", params={"photo_id": photoID})
    if resp is not None:
        return json.load(resp)['photo']
    else:
        return None


class Photo():

    def __init__(self, pd):
        self.title = pd['title']['_content']
        self.author = pd['owner']['username']
        self.userid = pd['owner']['nsid']
        self.tags = [tag["_content"] for tag in pd['tags']['tag']]
        self.numViews = int(pd['views'])
        self.commentcount = int(pd['comments']['_content'])
        self.url = pd['urls']['url'][0]['_content']
        self.thumbnailURL = self.makePhotoURL(pd)

    def makePhotoURL(self, pd, size="q"):
        url = "https://farm%s.staticflickr.com/%s/%s_%s_%s.jpg" % (
        pd['farm'], pd['server'], pd['id'], pd['secret'], size)
        return url

    def __str__(self):
        return "~~~ %s ~~~\nauthor: %s\nnumber of tags: %d\nviews: %d\ncomments: %d" % (
        self.title, self.author, len(self.tags), self.numViews, self.commentcount)

###################
##################


class spotiClient():
    import json
    # I'm going to create a client class to handle requests to spotify
    # including managing authorization.
    # This is different from Flickr where we just wrote one function

    def __init__(self):
        self.accessToken = None
        self.spotifyAuth()

    def spotifyAuth(self):
        """Method to actually handle authorization"""

        # Note: I put my client id and client secret in secrets.py
        # and told git to ignore that file. You should too.
        from secrets import CLIENT_ID, CLIENT_SECRET
        import base64

        # Following documentation in https://developer.spotify.com/web-api/authorization-guide/#client_credentials_flow
        #
        # Spotify expects:
        # the Authorization in the *header*,
        # A Base 64 encoded string that contains the client ID and client secret key. The field must have the format: Authorization: Basic <base64 encoded client_id:client_secret>
        # grant_type = "client_credentials" as a parameter

        # build the header
        authorization =  base64.standard_b64encode((CLIENT_ID + ':' + CLIENT_SECRET).encode())
        headers = {"Authorization":"Basic "+authorization.decode()}

        # encode the params dictionary, note it needs to be byte encoded
        params = {"grant_type" : "client_credentials"}
        encodedparams = urllib.urlencode(params).encode()

        # request goes to POST https://accounts.spotify.com/api/token
        request = urllib2.Request('https://accounts.spotify.com/api/token', data=encodedparams, headers=headers)
        resp = urllib2.urlopen(request)

        # I should do some error handling, but this is a quick example
        respdata = json.load(resp)
        self.accessToken = respdata['access_token']
        # Note that by default this token will expire in 60 minutes.
        # If your application will run longer, you will need a way to manage that.

    def apiRequest(self,version="v1",endpoint="search",item=None,params=None):
        """Method for API calls once authorized. By default, it will execute a search.

        See https://developer.spotify.com/web-api/endpoint-reference/ for endpoints

        Items, e.g., a track ID, are passed in via the item parameter.
        Parameters, e.g., search parameters, are passed in via the params dictionary"""

        if self.accessToken is None:
            print("Sorry, you must have an access token for this to work.")
            return {}

        baseurl = "https://api.spotify.com/"
        endpointurl = "%s%s/%s"%(baseurl,version,endpoint)

        # are there any params we need to pass in?
        if item is not None:
            endpointurl =  endpointurl + "/" + item
        if params is not None:
            fullurl = endpointurl + "?" + urllib.urlencode(params)

        headers = {"Authorization":"Bearer "+self.accessToken}
        request = urllib2.Request(fullurl, headers=headers)
        resp = urllib2.urlopen(request)

        # again, I should some error handling but I want to go back to making the practice exam
        return json.load(resp)

##################
################

class MainHandler(webapp2.RequestHandler):
    def get(self):
        vals = {}
        vals['page_title'] = "Greeting Page Response"
        song_name = self.request.get('songname')
        artist_name = self.request.get('artistname')

        if song_name and artist_name:
            lyrics = getLyrics(song_name, artist_name)
            #r = paralleldots.emotion(lyrics)['emotion']
            list_url = []
            photoIDs = getPhotoIDs(artist_name)
            for i in photoIDs:
                p_info = getPhotoInfo(i)
                obj = Photo(p_info)
                url = obj.makePhotoURL(pd=p_info)
                list_url.append(url)

            ###
            sclient = spotiClient()
            searchresult = sclient.apiRequest(params={"type": "artist", "q": artist_name})
            artist_id = searchresult['artists']['items'][0]['id']
            soloman = sclient.apiRequest(endpoint="artists", item=artist_id + "/top-tracks", params={"country": "ES"})
            tracklist = soloman['tracks']
            emp_list = []
            for i in tracklist:
                emp_list.append(i['name'])
            ####

            templatevals = {"lyr": lyrics, "urls": [], "top": emp_list}
            for i in range(1, 4):
                templatevals['urls'].append({"photo_url": list_url[i - 1]})


            template = JINJA_ENVIRONMENT.get_template('greetform.html')
            self.response.write(template.render(templatevals))
        else:
            vals['prompt'] = "Please enter a tag"
            template = JINJA_ENVIRONMENT.get_template('greetform.html')
            self.response.write(template.render(vals))


class GreetHandler(webapp2.RequestHandler):
    def get(self):
        vals = {}
        vals['page_title'] = "Greeting form"
        template = JINJA_ENVIRONMENT.get_template('greetform.html')
        self.response.write(template.render(vals))

application = webapp2.WSGIApplication([ \
                                        ('/greetings', GreetHandler),
                                        # ('/gresponse', GreetResponseHandler),
                                        ('/.*', MainHandler)
                                        ],
                                        debug=True)
