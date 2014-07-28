#!/bin/python2

import os
import sqlite3 as sql
import mutagen
import collections

dir = '/home/felix/Music'
#database_path = '../library.db'

database_path = '/srv/http/partyplayer/library.db'

def tree():
    return collections.defaultdict(tree)

try:
    os.remove(database_path)
except OSError:
    pass

db = sql.connect(database_path)
cur = db.cursor()
cur.execute("CREATE TABLE playlist(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, lft INTEGER, rgt INTEGER, info INTEGER)")
cur.execute("CREATE TABLE songs(id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT, vote INTEGER, played INTEGER)")
cur.execute("CREATE TABLE metadata(id var_char(16) PRIMARY KEY, value TEXT)")
cur.execute("INSERT INTO metadata VALUES ('prefix', '%s')" % (dir))
cur.execute('PRAGMA encoding="UTF-8";')

library_tree=tree()

for dirname, dirnames, filenames in os.walk(dir):
    # print path to all subdirectories first.
    #for subdirname in dirnames:
        #print os.path.join(dirname, subdirname)

    # print path to all filenames.

    
    
    for filename in filenames:
	if (filename.endswith(('.mp3','.flac','.m4a','.aac','.ogg'))):
		print filename
		path = os.path.join(dirname, filename)
        	#print path
		metadata = mutagen.File(path,easy=True)	
		title = os.path.splitext(filename)[0]
		try:
			title = metadata['title'][0].encode('utf-8').replace("'",r"''")
		except KeyError:
			print title

		artist = 'Unknown Artist'
		try:
			artist = metadata['artist'][0].encode('utf-8').replace("'",r"''")
		except KeyError:
			print artist
			

		album = 'Unknown Album'
		try:
			album = metadata['album'][0].encode('utf-8').replace("'",r"''")
		except KeyError:
			print album

		library_tree[artist][album][title] = path.replace("'",r"''")[len(dir):]


index=1
for artist in library_tree:
    artist_left = index
    index += 1
    for album in library_tree[artist]:
        album_left = index
        index += 1
        for title in library_tree[artist][album]:
            cur.execute("INSERT INTO songs VALUES (NULL, '%s', 0, 0)" % (library_tree[artist][album][title]))
            cur.execute("INSERT INTO playlist VALUES (NULL ,'%s','%d','%d', LAST_INSERT_ROWID())" % (title,index,index+1))
            index += 2

        cur.execute("INSERT INTO playlist VALUES (NULL,'%s','%d','%d', NULL)" % (album,album_left,index))
        index += 1

    cur.execute("INSERT INTO playlist VALUES (NULL, '%s','%d','%d', NULL)" % (artist,artist_left,index))
    index += 1

    
		#command = "INSERT INTO playlist (path, title, artist, album) VALUES('%s','%s','%s','%s')" % (path.replace("'",r"''"),title.replace("'",r"''"),artist.replace("'",r"''"),album.replace("'",r"''"))
		#cur.execute(command)

db.commit()
db.close()

    # Advanced usage:
    # editing the 'dirnames' list will stop os.walk() from recursing into there.
   # if '.git' in dirnames:
        # don't go into any .git directories.
      #  dirnames.remove('.git')
