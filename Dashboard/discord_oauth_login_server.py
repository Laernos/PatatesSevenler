"""
Example of using Discord OAuth to allow someone to
log in to your site. The scope of 'email+identify' only
lets you see their email address and basic user id.
"""
from requests_oauthlib import OAuth2Session
import getpass
from flask import Flask, request, redirect, session, render_template
import os
import pymongo
from pymongo import MongoClient

# Disable SSL requirement
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Settings for your app
base_discord_api_url = 'https://discordapp.com/api'
client_id = r'' # Get from https://discordapp.com/developers/applications
client_secret = ""
redirect_uri='http://localhost:8080/callback'
scope = ['identify', 'guilds']
token_url = 'https://discordapp.com/api/oauth2/token'
authorize_url = 'https://discordapp.com/api/oauth2/authorize'
cluster = MongoClient("")
db = cluster["discordveri"]
collection = db["uyeveri"]

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route("/")
def home():
    """
    Presents the 'Login with Discord' link
    """
    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)
    login_url, state = oauth.authorization_url(authorize_url)
    session['state'] = state
    print("Login url: %s" % login_url)
    return '<a href="' + login_url + '">Login with Discord</a>'

@app.route("/callback")
def oauth_callback():
    """
    The callback we specified in our app.
    Processes the code given to us by Discord and sends it back
    to Discord requesting a temporary access token so we can 
    make requests on behalf (as if we were) the user.
    e.g. https://discordapp.com/api/users/@me
    The token is stored in a session variable, so it can
    be reused across separate web requests.
    """
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
    print('Profile: %s' % response.json()['id'])
    response2 = discord2.get(base_discord_api_url + '/users/@me/guilds')
    print('Guilds: %s' % response2.json())
    post = {"_id": response.json()['id'], "sunucular": response2.json()}
    collection.insert_one(post)


    return render_template('index.html')



# Or run like this
# FLASK_APP=discord_oauth_login_server.py flask run -h 0.0.0.0 -p 8000
if __name__ == '__main__':
    app.run(host='localhost', port=8080)

