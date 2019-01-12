#!/usr/bin/env python3

import spotipy
import spotipy.util as util

import configparser
import datetime
import sys
import os

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
    conf_dir = os.environ['HOME'] + '/.config/dw-saver/'
    conf_file = conf_dir + 'dws.conf' if len(sys.argv) < 2 else sys.argv[1]
    config = configparser.ConfigParser()
    config.read_file(open(conf_file))

    user_name = config.get('Login', 'user_name')
    client_id = config.get('Login', 'client_id')
    client_secret = config.get('Login', 'client_secret')
    redirect_uri = config.get('Login', 'redirect_uri')

    scope = 'playlist-modify-public'
    tok = util.prompt_for_user_token(user_name, scope=scope,
                                     client_id=client_id, client_secret=client_secret,
                                     redirect_uri=redirect_uri,
                                     cache_path=conf_dir + 'cookie-' + user_name)

    sp = spotipy.Spotify(auth=tok)
    aggregate = lambda f, p: aggregate_spotify(sp, f, p)

    playlists = aggregate(lambda x: sp.user_playlists(*x), [user_name])
    discover_weekly = [p for p in playlists if is_discover_weekly(p)][0]
    tracks = sp.user_playlist_tracks(user_name, discover_weekly['uri'])

    track_ids = [item['track']['id'] for item in tracks['items']]

    other_pls = [p for p in playlists
                 if not is_discover_weekly(p)
                 and p['owner']['id'] == user_name]

    all_exists = False
    for p in other_pls:
        p_tracks = aggregate(lambda x: sp.user_playlist_tracks(*x), [user_name, p['uri']])
        # print(p['name'], 'has', len(p_tracks), 'tracks')
        other_ids = [item['track']['id'] for item in p_tracks]

        exists = True
        for t_id in track_ids:
            exists = exists and (t_id in other_ids)

        all_exists = all_exists or exists
        if all_exists:
            break

    if all_exists:
        print('Discover Weekly has already been saved')
    else:
        print('DW will be saved now')
        year = datetime.datetime.now().year
        week = datetime.datetime.now().isocalendar()[1]
        dw_name = 'Discover Weekly ' + str(week) + '/' + str(year)
        description = 'Automaticlly created playlist from discover weekly'
        resp = sp.user_playlist_create(user_name, dw_name)

        plist = resp['id']
        resp = sp.user_playlist_add_tracks(user_name, plist, track_ids)

        print('DW should be saved as', dw_name)
        # resp = sp.user_playlist_change_details(user_name, plist, description=description)

if __name__ == '__main__':
    main()
