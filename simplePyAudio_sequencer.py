import time
import math
import array
import librosa
import pyaudio     #sudo apt-get install python-pyaudio
import wave
import numpy
from threading import Thread
class MySeq():
    def __init__(self):
        fichier = open("congabass.csv","r")
        self.lines = fichier.readlines()
        self.tabEvents = []
        self.taboct = []
        self.tabAlts= []
        fichier.close()
        print (self.lines)
        self.readTempo()
        self.readEvents()
        print(len(self.tabEvents))
        self.readLoop()
    def readTempo(self):
        self.tempo = int(self.lines[0].split(";")[1])
        print (self.tempo)
    def readEvents(self):
        for line in self.lines:
            line =line.split(";")
            if line[1].isdigit() and line[0]!= "tempo" and line[0]!= "loop":
                event =line[2].replace("\n","")
                self.tabEvents.append(event)
                alt=line[4].replace("\n","")
                self.tabAlts.append(alt)
                oct = line[3].replace("\n","")
                self.taboct.append(oct)
        print (self.tabAlts)
        print (self.taboct)
        print (self.tabEvents)
    def readLoop(self):
        pass
    
class PlaySeq():
    def __init__(self,seq):
        
        self.seq=seq
        self.durationEvent = 60.0/self.seq.tempo/4.0
        fname ="synthbass2-ancien1.wav"
        self.wf = wave.open(fname, 'rb')
        self.framerate=self.wf.getframerate()
        print ("framerate",self.framerate)
        print ("channels",self.wf.getnchannels())
        self.p = pyaudio.PyAudio()
        self.chunk = 1024
        self.stream = self.p.open(format=self.p.get_format_from_width(self.wf.getsampwidth()),
#                     channels=self.wf.getnchannels(),
                    channels=1,
                    rate=self.wf.getframerate(),
                    output=True)
        self.LoadNote()
        self.play()

    def play(self):
        time0=time.time()
        eventIndex = 0

        while(True):
            t= time.time()-time0
            if t > eventIndex*self.durationEvent :
                event = self.seq.tabEvents[eventIndex%len(self.seq.tabEvents)]
                oct = self.seq.taboct[eventIndex%len(self.seq.taboct)]
                alt = self.seq.tabAlts[eventIndex%len(self.seq.tabAlts)]
                self.sendEvent(event,oct,alt)
                eventIndex+=1
    def sendEvent(self,event,oct,alt):
        sampleRoot=1
        SoundBinRoot =-24
        dict_events = {"LA":0,"SI":2,"DO":3,"RE":5,"MI":7,"FA":8,"SO":10}
        dict_alts = {"#":1,"b":-1,"":0}
        if event !="":
            pitch = dict_events.get(event,0)
            altpitch = dict_alts.get(alt,0)
            if oct=='':
                oct =0
            octpitch = 12*int(oct)
            note=self.SoundBinTab[pitch+altpitch+octpitch-sampleRoot+SoundBinRoot]
            self.stream.start_stream()
            self.stream.write(note)
            self.stream.stop_stream()
        else :
            pass
         
    def LoadNote(self):
        print ("loading note")
        self.La0 = b""
        self.SoundBinTab = []
        index = 0
        data = self.wf.readframes(self.chunk)
        print (len(data))
        elt = b""
        while index < 60.0/self.seq.tempo/8.0*44100.0/512.0:
            index+=1
            self.La0 += data
            data = self.wf.readframes(self.chunk)
        wavArrLa0 = numpy.frombuffer(self.La0, 'short')
        wavArrLa0=numpy.reshape(wavArrLa0,(2,int(len(self.La0)/4)),order="F")
        arrRos= wavArrLa0[0].astype(numpy.float32)
        print("note LA0 loaded")
        for index in range (-24,24):
            y_third = librosa.effects.pitch_shift(arrRos, sr=self.framerate, n_steps=index)
            bufThird = y_third.astype(numpy.short).tobytes()
            self.SoundBinTab.append(bufThird)
        print ('allNotesLoaded')
        
if __name__ =="__main__":
    seq = MySeq()
    PlaySeq(seq)
