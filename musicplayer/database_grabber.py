#!/bin/python2

import os
import sqlite3 as sql
import array

database_path = '/srv/http/partyplayer/library.db'

db = sql.connect(database_path)
cur = db.cursor()

def getArtists():

    results = []
    cur.execute("""
                SELECT node.title, node.id, (COUNT(parent.title) - 1) AS depth
                FROM playlist AS node, playlist AS parent
                WHERE node.lft BETWEEN parent.lft AND parent.rgt
                GROUP BY node.title
                HAVING depth = 0
                ORDER BY node.title
                """)
    rows = cur.fetchall()
    for row in rows:
        results.append(row)

    return results

def getAlbums(artist):

    results = []
    cur.execute("""
                SELECT node.title, node.id, (COUNT(parent.title) - (sub_tree.depth + 1)) AS depth2
                FROM playlist AS node, playlist AS parent,playlist AS sub_parent,
                (
                    SELECT node.title, (COUNT(parent.title) - 1) AS depth
                    FROM playlist AS node, playlist AS parent
                    WHERE node.lft BETWEEN parent.lft AND parent.rgt
                    AND node.id = '%d'
                    GROUP BY node.title
                    HAVING depth = 0
                    ORDER BY node.lft
                )AS sub_tree
                WHERE node.lft BETWEEN parent.lft AND parent.rgt
                AND node.lft BETWEEN sub_parent.lft AND sub_parent.rgt
                AND sub_parent.title = sub_tree.title
                GROUP BY node.title
                HAVING depth2 = 1
                ORDER BY node.title
                """ % (artist))
    rows = cur.fetchall()
    for row in rows:
        results.append(row)

    return results

def getSongs(album):
    results = []
    cur.execute("""
                SELECT node.title, node.info, (COUNT(parent.title) - (sub_tree.depth + 1)) AS depth2
                FROM playlist AS node, playlist AS parent,playlist AS sub_parent,
                (
                    SELECT node.title, (COUNT(parent.title) - 1) AS depth
                    FROM playlist AS node, playlist AS parent
                    WHERE node.lft BETWEEN parent.lft AND parent.rgt
                    AND node.id = '%d'
                    GROUP BY node.title
                    HAVING depth = 1
                    ORDER BY node.lft
                )AS sub_tree
                WHERE node.lft BETWEEN parent.lft AND parent.rgt
                AND node.lft BETWEEN sub_parent.lft AND sub_parent.rgt
                AND sub_parent.title = sub_tree.title
                GROUP BY node.title
                HAVING depth2 = 1
                ORDER BY node.title
                """ % (album))
    rows = cur.fetchall()
    for row in rows:
        results.append(row)

    return results

def getNextSong():
    cur.execute('SELECT * FROM songs WHERE vote = (SELECT MAX(vote) FROM songs) AND played = (SELECT MIN(played) FROM songs) ORDER BY RANDOM() LIMIT 1')
    song = cur.fetchone()
    cur.execute('UPDATE songs SET played = played+1 WHERE id = %d' % song[0])
    cur.execute('UPDATE songs SET vote = 0 WHERE id = %d' % song[0])
    db.commit()
    return song[1]


artists = getArtists();
for artist in artists:
    print artist[0]

print ''

albums = getAlbums(artists[1][1])
for album in albums:
    print album[0]

print ''

songs = getSongs(albums[0][1])
for song in songs:
    print song[0]

print getNextSong()

db.close()
