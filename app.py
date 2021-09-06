import os
from flask import Flask, session, request, redirect, render_template, flash, url_for
from flask_session import Session
import spotipy
import uuid
import json
from pprint import pprint
import config

from spotipy.client import Spotify 

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)

caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

def session_cache_path():
    return caches_folder + session.get('uuid')
# AUTHORIZATION and SIGN-IN/SIGN-OUT
@app.route('/')
def index():  
    if not session.get('uuid'):
        # Step 1. Visitor is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(client_id=config.SPOTIPY_CLIENT_ID, 
                                                client_secret=config.SPOTIPY_CLIENT_SECRET, 
                                                redirect_uri=config.SPOTIPY_REDIRECT_URI, 
                                                scope= config.SCOPE,
                                                cache_handler=cache_handler, 
                                                show_dialog=True)

    if request.args.get("code"):
        # Step 3. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return render_template("/signIn.html", auth_url= auth_url)

    # Step 4. Signed in, start page (selecct duplicate or search)
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    return render_template('/start.html') # START: SELECT SEARCH or DUP

@app.route('/sign_out')
def sign_out():
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove(session_cache_path())
        session.clear()
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))
    return redirect('/')


@app.route('/about')
def about():
    return render_template('/about.html')
###HELPER FUNCTIONS###
def remove_val(the_list, val):
   return [value for value in the_list if value != val]

def getTracks(playlist_id):
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(client_id=config.SPOTIPY_CLIENT_ID, 
                                                client_secret=config.SPOTIPY_CLIENT_SECRET, 
                                                redirect_uri=config.SPOTIPY_REDIRECT_URI, 
                                                scope= config.SCOPE,
                                                cache_handler=cache_handler, 
                                                show_dialog=True)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    results = spotify.playlist_items(playlist_id, 
                                    offset=0,
                                    fields='items.track.id',
                                    additional_types=['track'])
    results = results['items']
    li = []
    for i in range(len(results)):
        li.append((playlist_id, results[i]['track']['id']))
    return li
def getTracks_(playlist_id):
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(client_id=config.SPOTIPY_CLIENT_ID, 
                                                client_secret=config.SPOTIPY_CLIENT_SECRET, 
                                                redirect_uri=config.SPOTIPY_REDIRECT_URI, 
                                                scope= config.SCOPE,
                                                cache_handler=cache_handler, 
                                                show_dialog=True)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    results = spotify.playlist_items(playlist_id, 
                                    offset=0,
                                    fields='items.track.id',
                                    additional_types=['track'])
    results = results['items']
    li = []
    for i in range(len(results)):
        li.append(results[i]['track']['id'])
    return li 

def checkDup(li):
    seen = set()
    seen_add = seen.add
    seen_more = set( x for x in li if x in seen or seen_add(x))
    return list(seen_more)

def convert(tup, di):
     for a, b in tup:
         di.setdefault(a, []).append(b)
     return di

def getTrackInfo(id):
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(client_id=config.SPOTIPY_CLIENT_ID, 
                                                client_secret=config.SPOTIPY_CLIENT_SECRET, 
                                                redirect_uri=config.SPOTIPY_REDIRECT_URI, 
                                                scope= config.SCOPE,
                                                cache_handler=cache_handler, 
                                                show_dialog=True)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    trackURN = "spotify:track:{}".format(id)
    track = spotify.track(trackURN)
    trackOpen = track['album']['external_urls']['spotify']
    trackName = track['name']
    trackImageUrl = track['album']['images'][1]['url']
    return (trackName,trackImageUrl,trackOpen)
def getTrackInfo_(id):
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(client_id=config.SPOTIPY_CLIENT_ID, 
                                                client_secret=config.SPOTIPY_CLIENT_SECRET, 
                                                redirect_uri=config.SPOTIPY_REDIRECT_URI, 
                                                scope= config.SCOPE,
                                                cache_handler=cache_handler, 
                                                show_dialog=True)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    trackURN = "spotify:track:{}".format(id)
    track = spotify.track(trackURN)
    trackArtistId=track['album']['artists'][0]['id']
    return trackArtistId
    
def getPlayInfo(id):
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(client_id=config.SPOTIPY_CLIENT_ID, 
                                                client_secret=config.SPOTIPY_CLIENT_SECRET, 
                                                redirect_uri=config.SPOTIPY_REDIRECT_URI, 
                                                scope= config.SCOPE,
                                                cache_handler=cache_handler, 
                                                show_dialog=True)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    URN = "spotify:user:spotifycharts:playlist:{}".format(id)
    result = spotify.playlist(URN)
    plOpen =result['external_urls']['spotify']
    plName = result['name']
    plimageURL= result['images'][0]['url']
    return (plName,plimageURL, plOpen)
   
################

###CHECK DUPS###
@app.route('/playlists')  # Provide dictionary of USER PLAYLISTS 
def playlists():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(client_id=config.SPOTIPY_CLIENT_ID, 
                                                client_secret=config.SPOTIPY_CLIENT_SECRET, 
                                                redirect_uri=config.SPOTIPY_REDIRECT_URI, 
                                                scope= config.SCOPE,
                                                cache_handler=cache_handler, 
                                                show_dialog=True)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    pl = spotify.current_user_playlists()['items']
    pl_ = {}
    for i, item in enumerate(pl):
        pl_.update({item['name'] : item['images'][0]['url']})
    
    return render_template('formCheck.html', 
                            data = pl_)

@app.route("/NoSelection")
def noSelection():
    return render_template("noSelect.html")


@app.route("/formCheckHandler" , methods=['GET', 'POST'])
def formCheckHandler():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(client_id=config.SPOTIPY_CLIENT_ID, 
                                                client_secret=config.SPOTIPY_CLIENT_SECRET, 
                                                redirect_uri=config.SPOTIPY_REDIRECT_URI, 
                                                scope= config.SCOPE,
                                                cache_handler=cache_handler, 
                                                show_dialog=True)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    pl = spotify.current_user_playlists()['items']
    pl_ = {}
    for i, item in enumerate(pl):
        pl_.update({item['name'] : item['id']})
    select = request.form.getlist('check[]') 
    if select == []:
        return redirect('/NoSelection')
    
    # GET USER SELECTED PLAYLIST IDS in a LIST
    finalPL = []
    for i in select:
        if i in pl_.keys():
            x = pl_[i]
            finalPL.append(x)
    # GET DICTIONARY of {pl ID: [trackIDs]}
    keyval = []
    for val in range(len(finalPL)):
        tracks = getTracks(finalPL[val])
        keyval = keyval + tracks
    li = keyval
    dictionary = {}
    z = convert(li, dictionary)
    
    # GET SONGS THAT SHOW MORE THAN ONCE
    tracklist=[]
    for val in range(len(finalPL)):
        track = getTracks_(finalPL[val])
        tracklist = track + tracklist
    tracklist = remove_val(tracklist, None)
    dup = checkDup(tracklist)
    if dup == []:
        return render_template('noDup.html') 
    
    # GET DICTIONARY of {song: [pl name]}
    match = {}
    for k, v in z.items():
        for elem in v:
            if elem in dup:
                if elem in match:
                    match[elem].append(k)
                else:
                    match[elem] = [k]
    info = {} 
    for m, n in match.items():
        m_ = getTrackInfo(m)[0]
        info[m_]={}
        info[m_]['trackURL'] = getTrackInfo(m)[1]
        info[m_]['trackOpen'] = getTrackInfo(m)[2]
        info[m_]["playlists"]=[]
        for ele in n:
            info[m_]["playlists"].append({'name':getPlayInfo(ele)[0], 'url':getPlayInfo(ele)[1], 'plOpen':getPlayInfo(ele)[2]})
    
    return render_template("display_00.html", info = info) # Send duplicates to display 
###############

###SEARCH###
@app.route('/playlists_')  # Provide dictionary of USER PLAYLISTS 
def playlists_():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(client_id=config.SPOTIPY_CLIENT_ID, 
                                                client_secret=config.SPOTIPY_CLIENT_SECRET, 
                                                redirect_uri=config.SPOTIPY_REDIRECT_URI, 
                                                scope= config.SCOPE,
                                                cache_handler=cache_handler, 
                                                show_dialog=True)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    pl = spotify.current_user_playlists()['items']
    pl_ = {}
    for i, item in enumerate(pl):
        pl_.update({item['name'] : item['images'][0]['url']})
    
    return render_template('formCheck_.html', 
                            data = pl_)

@app.route("/NoSelection_")
def noSelection_():
    return render_template("noSelect_.html")

@app.route('/formCheckHandler_', methods=['GET', 'POST'])
def formCheckHandler_():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(client_id=config.SPOTIPY_CLIENT_ID, 
                                                client_secret=config.SPOTIPY_CLIENT_SECRET, 
                                                redirect_uri=config.SPOTIPY_REDIRECT_URI, 
                                                scope= config.SCOPE,
                                                cache_handler=cache_handler, 
                                                show_dialog=True)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    pl = spotify.current_user_playlists()['items']
    pl_ = {}
    for i, item in enumerate(pl):
        pl_.update({item['name'] : item['id']})
    select = request.form.getlist('check[]')
    if select == []:
        return redirect('/NoSelection_')
    finalPL = [] 
    
    # GET USER SELECTED PLAYLISTS in a LIST
    for i in select:
        if i in pl_.keys():
            x = pl_[i]
            finalPL.append(x)
    # GET DICTIONARY of {pl name: [tracks]}
    keyval = []
    for val in range(len(finalPL)):
        tracks = getTracks(finalPL[val])
        keyval = keyval + tracks
    li = keyval
    dictionary = {}
    z = convert(li, dictionary)
    for k in z:
        z[k] = remove_val(z[k], None)
    
    artistName = request.form.get("artistName")
    songName = request.form.get("songName")
    
    if artistName == "" or songName =="":
        return render_template("missing_.html")

    q=songName
    results = spotify.search(q=q, type='track')
    results_ = results['tracks']['items']
    # if items is empty 
    matchSongID = results['tracks']['items'][0]['id']
    matchSong = results['tracks']['items'][0]['name']
    matchName = results['tracks']['items'][0]['album']['artists'][0]['name']

    if results_ == []:
        return render_template("noSong.html")
    search=[]
    for x in range(len(results_)):
        res = results_[x]['album']['artists'][0]['name']
        if res.upper() == artistName.upper():
            search.append(results_[x]['id'])
    

    # GET DICTIONARY of {song: [pl name]}
    match = {}
    for k, v in z.items():
        for elem in v:
            if elem in search:
                if elem in match:
                    match[elem].append(k)
                else:
                    match[elem] = [k]
    if match == {}:
        return render_template("notFound.html" , songName=songName.upper(), artistName=artistName.upper())
    
    info = {} 
    for m, n in match.items():
        m_ = getTrackInfo(m)[0]
        info[m_]={}
        info[m_]['trackURL'] = getTrackInfo(m)[1]
        info[m_]['trackOpen'] = getTrackInfo(m)[2]
        info[m_]["playlists"]=[]
        for ele in n:
            info[m_]["playlists"].append({'name':getPlayInfo(ele)[0], 'url':getPlayInfo(ele)[1], 'plOpen':getPlayInfo(ele)[2]})
    
    return render_template("display_01.html", info = info) # Send to display 
##############


######FIND ARTIST#######
@app.route('/playlists_0')  # Provide dictionary of USER PLAYLISTS 
def playlists_0():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(client_id=config.SPOTIPY_CLIENT_ID, 
                                                client_secret=config.SPOTIPY_CLIENT_SECRET, 
                                                redirect_uri=config.SPOTIPY_REDIRECT_URI, 
                                                scope= config.SCOPE,
                                                cache_handler=cache_handler, 
                                                show_dialog=True)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    pl = spotify.current_user_playlists()['items']
    pl_ = {}
    for i, item in enumerate(pl):
        pl_.update({item['name'] : item['images'][0]['url']})
    
    return render_template('formCheck_0.html', 
                            data = pl_)

@app.route("/NoSelection_0")
def noSelection_0():
    return render_template("noSelect_0.html")

@app.route('/formCheckHandler_0', methods=['GET', 'POST'])
def formCheckHandler_0():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(client_id=config.SPOTIPY_CLIENT_ID, 
                                                client_secret=config.SPOTIPY_CLIENT_SECRET, 
                                                redirect_uri=config.SPOTIPY_REDIRECT_URI, 
                                                scope= config.SCOPE,
                                                cache_handler=cache_handler, 
                                                show_dialog=True)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    pl = spotify.current_user_playlists()['items']
    pl_ = {}
    for i, item in enumerate(pl):
        pl_.update({item['name'] : item['id']})
    select = request.form.getlist('check[]')
    if select == []:
        return redirect('/NoSelection_0')
    finalPL = [] 
    
    # GET USER SELECTED PLAYLISTS in a LIST
    for i in select:
        if i in pl_.keys():
            x = pl_[i]
            finalPL.append(x)
    # GET DICTIONARY of {pl name: [tracks]}
    keyval = []
    for val in range(len(finalPL)):
        tracks = getTracks(finalPL[val])
        keyval = keyval + tracks
    li = keyval
    dictionary = {}
    z = convert(li, dictionary)
    for k in z:
        z[k] = remove_val(z[k], None)
    artistName = request.form.get("artistName")
    if artistName == "":
        return render_template("missing_01.html")

    q=artistName
    results = spotify.search(q=q, type='artist')
    results = results['artists']['items']
    artistId = []
    for x in results:
        artistId.append(x['id'])

    if artistId == []:
        return render_template("noArtist.html")

    
    for k,v in z.items():
        for elem in range(len(v)):
            artId = getTrackInfo_(v[elem])
            v[elem] = (v[elem], artId)
    match = {} 
    for k,v in z.items():
        match[k]=[]
        for el in v:
            if el[1] in artistId:
                match[k].append(el[0])  
            else:
                 continue  
                
    info ={}
    for m, n in match.items():
        m_ = getPlayInfo(m)[0]
        info[m_]={}
        info[m_]['plURL'] = getPlayInfo(m)[1]
        info[m_]['plOpen'] = getPlayInfo(m)[2]
        info[m_]["tracks"]=[]
    
        if n == []:
            continue
        else:
            for ele in n:
                info[m_]["tracks"].append({'name':getTrackInfo(ele)[0], 'url':getTrackInfo(ele)[1], 'trackOpen':getTrackInfo(ele)[2]})

    return render_template("display_02.html", info=info, artistName=artistName.upper())
##################
if __name__=='__main__':
    app.run(debug=True)
