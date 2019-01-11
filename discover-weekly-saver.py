import spotipy
import spotipy.util as util

import configparser

config = configparser.ConfigParser()
config.read_file(open(r'dws.conf'))

user_name = config.get('Login', 'user_name')
client_id = config.get('Login', 'client_id')
client_secret = config.get('Login', 'client_secret')
redirect_uri = config.get('Login', 'redirect_uri')

print(user_name, client_id, client_secret, redirect_uri)

scope = 'playlist-modify-public'
util.prompt_for_user_token(user_name, scope=scope,
                           client_id=client_id, client_secret=client_secret,
                           redirect_uri=redirect_uri)
