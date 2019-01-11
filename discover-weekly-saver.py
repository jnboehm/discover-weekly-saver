import spotipy
import spotipy.util as util

import configparser

def is_discover_weekly(playlist_dict):
    return playlist_dict['name'] == 'Discover Weekly'

def aggregate_spotify(sp, api_fun, params):
    resp = api_fun(params)
    agg = resp['items']

    resp = sp.next(resp)
    while resp is not None:
        agg += resp['items']
        resp = sp.next(resp)

    return agg

def main():
    config = configparser.ConfigParser()
    config.read_file(open(r'dws.conf'))

    user_name = config.get('Login', 'user_name')
    client_id = config.get('Login', 'client_id')
    client_secret = config.get('Login', 'client_secret')
    redirect_uri = config.get('Login', 'redirect_uri')

    scope = 'playlist-modify-public'
    tok = util.prompt_for_user_token(user_name, scope=scope,
                                     client_id=client_id, client_secret=client_secret,
                                     redirect_uri=redirect_uri)

    sp = spotipy.Spotify(auth=tok)
    aggregate = lambda f, p: aggregate_spotify(sp, f, p)

    playlists = aggregate(lambda x: sp.user_playlists(*x), [user_name])
    discover_weekly = [p for p in playlists if is_discover_weekly(p)][0]

if __name__ == '__main__':
    main()
