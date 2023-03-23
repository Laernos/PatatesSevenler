from requests_oauthlib import OAuth2Session
import getpass
from flask import Flask, request, redirect, session, render_template
import os
import pymongo
from pymongo import MongoClient

# Disable SSL requirement
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

base_discord_api_url = 'https://discordapp.com/api'
client_id = r'' # Get from https://discordapp.com/developers/applications
client_secret = ""
redirect_uri='https://dash.patatessevenler.com/callback'
scope = ['identify', 'guilds']
token_url = 'https://discordapp.com/api/oauth2/token'
authorize_url = 'https://discordapp.com/api/oauth2/authorize'
cluster = MongoClient("")
db = cluster["discordveri"]
collection = db["uyeveri"]
db2 = cluster["myFirstDatabase"]
collection2 = db2["memberstats"]
project_root = os.path.dirname(os.path.realpath('__file__'))
template_path = os.path.join(project_root, 'templates')
static_path = os.path.join(project_root, 'static')
app = Flask(__name__, template_folder=template_path, static_folder=static_path)
app.secret_key = os.urandom(24)

@app.route("/")
def home():
    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)
    login_url, state = oauth.authorization_url(authorize_url)
    session['state'] = state
    return render_template('login.html', login= login_url)

@app.route("/callback", methods=["GET", "POST"])
def oauth_callback():
    discord = OAuth2Session(client_id, redirect_uri=redirect_uri, state=session['state'], scope=scope)
    token = discord.fetch_token(
        token_url,
        client_secret=client_secret,
        authorization_response=request.url,
    )
    session['discord_token'] = token


    discord2 = OAuth2Session(client_id, token=session['discord_token'])
    response = discord2.get(base_discord_api_url + '/users/@me')
    # https://discordapp.com/developers/docs/resources/user#user-object-user-structure
    id = response.json()['id']
    session['id'] = id
    avatar = response.json()['avatar']
    session['avatar'] = avatar
    session['username'] = response.json()['username']
    response2 = discord2.get(base_discord_api_url + '/users/@me/guilds')
    collection.delete_one({"uyeid": id})
    post = {"uyeid": response.json()['id'],"username": response.json()['username'], "sunucular": response2.json()}
    collection.insert_one(post)
    return redirect("/dash")

@app.route("/dash", methods=["GET", "POST"])
def dash():
    id = session['id']
    avatar = session['avatar']

    results = collection2.find({"userID": id})
    for result in results:
        try:
            mesaj = result["totalChatStats"]
        except:
            mesaj = "0"

    results = collection2.find({"userID": id})
    for x in results:
        try:
            haftamesaj = x["chatStats"]['592651806362959895']
        except:
            haftamesaj = "0"

    
    results = collection2.find({"userID": id})
    for result in results:
        try:
            millis = result["totalVoiceStats"]
            millis = int(millis)
            seconds=(millis/1000)%60
            seconds = int(seconds)
            minutes=(millis/(1000*60))%60
            minutes = int(minutes)
            hours=(millis/(1000*60*60))
            hours = int(hours)
        except:
            hours = "0"
            minutes = "0"
            seconds = "0"
        
    
    results = collection2.find({"userID": id})
    for x in results:
        try:
            milli2 = x["voiceStats"]['592651874528919564']
            milli2 = int(milli2)
            second2=(milli2/1000)%60 
            second2 = int(second2)
            minute2=(milli2/(1000*60))%60
            minute2 = int(minute2)
            hour2=(milli2/(1000*60*60))
            hour2 = int(hour2)
        except:
            hour2 = "0"
            minute2 = "0"
            second2 = "0"
        
    return render_template('index.html', username= session['username'], avatar= f'https://cdn.discordapp.com/avatars/{id}/{avatar}.png', hours= hours, minutes= minutes, mesaj= mesaj, hour2= hour2, minute2= minute2, haftamesaj= haftamesaj)

application = app



