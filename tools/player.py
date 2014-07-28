#!/bin/python2

import sqlite3 as sql
import time
import sys
import user
import vlc
from PyQt4 import QtGui, QtCore
import ctypes



class Player(QtGui.QMainWindow):
    """A simple Media Player using VLC and Qt
    """

    database_path = '/srv/http/partyplayer/library.db'
    choose_song_delay = 5000

    def __init__(self, master=None):
        QtGui.QMainWindow.__init__(self, master)
        self.setWindowTitle("Media Player")

        # creating a basic vlc instance
        self.instance = vlc.Instance()
        # creating an empty vlc media player
	
	self.mediaplayer = self.instance.media_player_new()

	self.songqueue = self.instance.media_list_new()
        self.medialistplayer = self.instance.media_list_player_new()
	self.medialistplayer.set_media_player(self.mediaplayer)	
	self.medialistplayer.set_media_list(self.songqueue)
	
        self.createUI()
        self.isPaused = False

	self.songChosen = False

        self.vlc_events = self.mediaplayer.event_manager()
        self.vlc_events.event_attach(vlc.EventType.MediaPlayerEndReached, self.SongFinished)

        self.songFetcher = self.nextSongGenerator()

        db = sql.connect(self.database_path)
        cur = db.cursor()
        cur.execute('SELECT value FROM metadata')
        self.prefix = cur.fetchone()[0]
        db.close()
        
    def createUI(self):
        """Set up the user interface, signals & slots
        """
        self.widget = QtGui.QWidget(self)
        self.setCentralWidget(self.widget)

        # In this widget, the video will be drawn
        if sys.platform == "darwin": # for MacOS
            self.videoframe = QtGui.QMacCocoaViewContainer(0)
        else:
            self.videoframe = QtGui.QFrame()
        self.palette = self.videoframe.palette()
        self.palette.setColor (QtGui.QPalette.Window,
                               QtGui.QColor(0,0,0))
        self.videoframe.setPalette(self.palette)
        self.videoframe.setAutoFillBackground(True)

        self.positionslider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.positionslider.setToolTip("Position")
        self.positionslider.setMaximum(1000)
        self.connect(self.positionslider,
                     QtCore.SIGNAL("sliderMoved(int)"), self.setPosition)

        self.hbuttonbox = QtGui.QHBoxLayout()
        self.playbutton = QtGui.QPushButton("Play")
        self.hbuttonbox.addWidget(self.playbutton)
        self.connect(self.playbutton, QtCore.SIGNAL("clicked()"),
                     self.PlayPause)

        self.stopbutton = QtGui.QPushButton("Stop")
        self.hbuttonbox.addWidget(self.stopbutton)
        self.connect(self.stopbutton, QtCore.SIGNAL("clicked()"),
                     self.Stop)

        self.nextbutton = QtGui.QPushButton("Next")
        self.hbuttonbox.addWidget(self.nextbutton)
        self.connect(self.nextbutton, QtCore.SIGNAL("clicked()"),
                     self.chooseNextSong)

        self.hbuttonbox.addStretch(1)
        self.volumeslider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.volumeslider.setMaximum(100)
        self.volumeslider.setValue(self.mediaplayer.audio_get_volume())
        self.volumeslider.setToolTip("Volume")
        self.hbuttonbox.addWidget(self.volumeslider)
        self.connect(self.volumeslider,
                     QtCore.SIGNAL("valueChanged(int)"),
                     self.setVolume)

        self.vboxlayout = QtGui.QVBoxLayout()
        self.vboxlayout.addWidget(self.videoframe)
        self.vboxlayout.addWidget(self.positionslider)
        self.vboxlayout.addLayout(self.hbuttonbox)

        self.widget.setLayout(self.vboxlayout)

        open = QtGui.QAction("&Open", self)
        self.connect(open, QtCore.SIGNAL("triggered()"), self.OpenFile)
        exit = QtGui.QAction("&Exit", self)
        self.connect(exit, QtCore.SIGNAL("triggered()"), sys.exit)
        menubar = self.menuBar()
        filemenu = menubar.addMenu("&File")
        filemenu.addAction(open)
        filemenu.addSeparator()
        filemenu.addAction(exit)

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(200)
        self.connect(self.timer, QtCore.SIGNAL("timeout()"),
                     self.updateUI)

    def PlayPause(self):
        """Toggle play/pause status
        """
        if self.mediaplayer.is_playing():
            self.medialistplayer.pause()
            self.playbutton.setText("Play")
            self.isPaused = True
        else:
            if self.medialistplayer.play() == -1:
                self.OpenFile()
                return
            self.medialistplayer.play()
            self.playbutton.setText("Pause")
            self.timer.start()
            self.isPaused = False

    def Stop(self):
        """Stop player
        """
        self.mediaplayer.stop()
        self.playbutton.setText("Play")

    def chooseNextSong(self):
            song = next(self.songFetcher)
	    print song
            self.OpenFile(song)

    def nextSongGenerator(self):
        while True:
                db = sql.connect(self.database_path)
                cur = db.cursor()
                cur.execute('SELECT * FROM songs WHERE vote = (SELECT MAX(vote) FROM songs) AND played = (SELECT MIN(played) FROM songs) ORDER BY RANDOM() LIMIT 1')
                song = cur.fetchone()
                cur.execute('UPDATE songs SET played = played+1 WHERE id = %d' % song[0])
                cur.execute('UPDATE songs SET vote = 0 WHERE id = %d' % song[0])
                db.commit()
                db.close()
                yield self.prefix + song[1]

    def OpenFile(self, filename=None):
        """Open a media file in a MediaPlayer
        """
        if filename is None:
            filename = QtGui.QFileDialog.getOpenFileName(self, "Open File", user.home)
        if not filename:
            return

        # create the media
        self.media = self.instance.media_new(unicode(filename))
        
        # put the media in the media player

        self.songqueue.add_media(self.media)

        # parse the metadata of the file
        self.media.parse()
        # set the title of the track as window title
        self.setWindowTitle(self.media.get_meta(0))
	self.songThreshold = (self.media.get_duration() - self.choose_song_delay) / float(self.media.get_duration())

        # the media player has to be 'connected' to the QFrame
        # (otherwise a video would be displayed in it's own window)
        # this is platform specific!
        # you have to give the id of the QFrame (or similar object) to
        # vlc, different platforms have different functions for this
        if sys.platform == "linux2": # for Linux using the X Server
            self.mediaplayer.set_xwindow(self.videoframe.winId())
        elif sys.platform == "win32": # for Windows
            self.mediaplayer.set_hwnd(self.videoframe.winId())
        elif sys.platform == "darwin": # for MacOS
            self.mediaplayer.set_nsobject(self.videoframe.winId())

    def setVolume(self, Volume):
        """Set the volume
        """
        self.mediaplayer.audio_set_volume(Volume)

    def setPosition(self, position):
        """Set the position
        """
        # setting the position to where the slider was dragged
        self.mediaplayer.set_position(position / 1000.0)
        # the vlc MediaPlayer needs a float value between 0 and 1, Qt
        # uses integer variables, so you need a factor; the higher the
        # factor, the more precise are the results
        # (1000 should be enough)

    def updateUI(self):
        """updates the user interface"""
        # setting the slider to the desired position
        self.positionslider.setValue(self.mediaplayer.get_position() * 1000)

	if(self.mediaplayer.get_position() > self.songThreshold and not self.songChosen):
		self.chooseNextSong()
		self.songChosen = True

        if not self.mediaplayer.is_playing():
            # no need to call this function if nothing is played
            self.timer.stop()
            if not self.isPaused:
                # after the video finished, the play button stills shows
                # "Pause", not the desired behavior of a media player
                # this will fix it
                self.Stop()
                
    @vlc.callbackmethod
    def SongFinished(self, data):
	self.songChosen = False


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    player = Player()
    player.show()
    player.resize(640, 480)
    player.chooseNextSong()
    player.PlayPause()
    sys.exit(app.exec_())

