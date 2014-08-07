# -*- coding: utf-8 -*-

import pyaudio
import wave
import numpy
import struct
import xlwt
import pyfftw.interfaces.numpy_fft as fftw

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 10
WAVE_OUTPUT_FILENAME = "output.wav"

class RecordThread(QtCore.QThread):

    def __init__(self, plot):
        QtCore.QThread.__init__(self)
        self.plot = plot
        self.p = pyaudio.PyAudio()

        self.stream = self.p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

        
        print("* recording")

        self.frames = []

    def run(self):

        FRAMES_USED = 3

        #for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        while True:
            data = self.stream.read(CHUNK)
            self.frames.append(data)
            if(len(self.frames) >= FRAMES_USED):
                data_frames = self.frames[:FRAMES_USED]
                self.frames = self.frames[FRAMES_USED:]
                result = self.do_fft(data_frames)
                #result = numpy.subtract(result,numpy.median(result))
                result = self.smooth(result,64)
                result = numpy.clip(result,0,10)
                self.plot.listDataItems()[0].setData(result)
        

        print("* done recording")

        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()


    def do_fft(self, data_frames):

        fmt = "%dH"%(len(data_frames[0])/2)
        data = ()
        for frame in data_frames:
            data += struct.unpack(fmt, frame)

        data = numpy.array(data, dtype='h')

        fourier = fftw.rfft(data)
        ffty = numpy.abs(fourier[0:len(fourier)/2])/1000
        ffty1=ffty[:len(ffty)/2]
        ffty2=ffty[len(ffty)/2::]+2
        ffty2=ffty2[::-1]
        ffty=ffty1+ffty2
        ffty=numpy.log(ffty)-2
           
        fourier = list(ffty)[4:-4]
        fourier = fourier[:len(fourier)/2]

        return fourier

    def smooth(self, data, parts):
        data_parts = numpy.array_split(data,parts)
        #mean = numpy.mean(data_parts,1)
        mean = list()
        for part in data_parts:
            mean.append(numpy.mean(part))
            
        return mean



app = QtGui.QApplication([])

win = pg.GraphicsWindow(title="Basic plotting examples")
win.resize(1000,600)
win.setWindowTitle('pyqtgraph example: Plotting')

pg.setConfigOptions(antialias=True)

p1 = win.addPlot(title="Basic array plotting", y=None)

recorder = RecordThread(p1)
#win.threads.append(recorder)
recorder.start()

QtGui.QApplication.instance().exec_()

