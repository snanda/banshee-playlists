import os, urllib, urlparse
import sqlite3


BANSHEE_DB = "/home/sameer/.config/banshee-1/banshee.db"
M3U_OUT_DIR = "/Music/playlists"

PLAYLISTS_TABLE = 'CorePlaylists'
PLAYLIST_ENTRIES_TABLE = 'CorePlaylistEntries'

SMART_PLAYLISTS_TABLE = 'CoreSmartPlaylists'
SMART_PLAYLISTS_ENTRIES_TABLE = 'CoreSmartPlaylistEntries'

SKIP_PLAYLISTS = ['Recently Added', 'Unheard']

M3U_FORMAT_DESCRIPTOR = "#EXTM3U"
M3U_RECORD_MARKER = "#EXTINF"


def create_m3u(playlist, tracks):
    print 'Creating M3U playlist for', playlist

    with open(os.path.join(M3U_OUT_DIR, playlist + '.m3u'), 'w') as f:
        f.write(''.join([M3U_FORMAT_DESCRIPTOR, '\n']))

        for track in tracks:
	    title = track['Title']

	    artist_id = track['ArtistID']
	    artist = find_artist(artist_id)

	    path = track['Uri']
	    path = urlparse.urlparse(path).path
	    path = urllib.url2pathname(path)

	    if artist and title:
	        f.write(''.join([M3U_RECORD_MARKER, ':', artist, ' - ', title, '\n']))
	    else:
	        f.write(''.join([M3U_RECORD_MARKER, ':', os.path.basename(path), '\n']))
	    
	    print path
            f.write(''.join([path, "\n"]))
    

def find_artist(artist_id):
    c.execute("SELECT Name from %s WHERE ArtistID is %d" % ('CoreArtists', artist_id))
    return c.fetchone()['Name']


def find_track(track_id):
    c.execute("SELECT * from %s WHERE TrackID is %d" % ('CoreTracks', track_id))
    return c.fetchone()
	

def find_playlist_entries(p_dict):
    if p_dict['smart_playlist']:
	entries_table = SMART_PLAYLISTS_ENTRIES_TABLE
	entries_column = 'SmartPlaylistID'
    else:
	entries_table = PLAYLIST_ENTRIES_TABLE
	entries_column = 'PlaylistID'
    
    print 'Fetching tracks for', p_dict['name']
    tracks = []
    for row in c.execute("SELECT * from %s WHERE %s is %d" % (
		entries_table, entries_column, p_dict['playlist_id'])).fetchall():
	tracks.append(find_track(row['TrackID']))

    create_m3u(p_dict['name'], tracks)


def find_playlists(t, smart_playlist):
    for row in c.execute("SELECT * from %s" % t).fetchall():
	p_dict = {}

	name = row['Name']
	if name in SKIP_PLAYLISTS:
	    print 'Skipping playlist', name
	    continue

	# Duplicate name? Modify it, if so.
	if name in playlist_names:
	    name = name + str(i)

	playlist_names.append(name)
	p_dict['name'] = name

	p_dict['smart_playlist'] = smart_playlist
        if smart_playlist:
	    p_dict['playlist_id'] = row['SmartPlaylistID']
	else:
	    p_dict['playlist_id'] = row['PlaylistID']

	find_playlist_entries(p_dict)


conn = sqlite3.connect(BANSHEE_DB)
conn.row_factory = sqlite3.Row
c = conn.cursor()

i = 0
playlist_names = []

find_playlists(PLAYLISTS_TABLE, False)
find_playlists(SMART_PLAYLISTS_TABLE, True)
