#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lang import lang
import audiotools

def secsToTime(secs):
    m = int(secs) // 60
    s = int(secs) - 60*m
    
    ps = "0" if len(str(s)) == 1 else ""    
    return "{}:{}{}".format(m, ps, s)

class _BaseException(Exception):
    def __str__(self):
        return self.__unicode__().encode("utf-8")
    def __unicode__(self):
        return u"no message"
        
class CannotOpenDevice(_BaseException):
    def __init__(self, device="unknown"):
        _BaseException.__init__(self)
        self.device = device
    def __unicode__(self):
        return u"Cannot open device '{}'".format(self.device)
class CannotLoadDevice(_BaseException):
    def __init__(self, device="unknown", exception=None):
        _BaseException.__init__(self)
        self.device = device
        self.exc = exception
    def __unicode__(self):
        return u"Cannot load device '{}' ({})".format(self.device, "unknown exception" if self.exc == None else type(self.exc))
class CannotSaveTrack(_BaseException):
    def __init__(self, trackno=0, exception=None):
        _BaseException.__init__(self)
        self.trackno = trackno
        self.exc = exception
    def __unicode__(self):
        return u"Cannot save track #{} ({})".format(self.trackno, "unknown exception" if self.exc == None else type(self.exc))

class _Container():
    def __init__(self):
        self.at = None
    def save(self, track, path):
        try:
            self._save(path, track)
        except Exception as e:
            raise CannotSaveTrack(track.no, e)
    def _save(self, path, track):
        self.at.from_pcm(path, track._track)

class FlacContainer(_Container):
    def __init__(self):
        _Container.__init__(self)
        self.at = audiotools.FlacAudio
class MP3Container(_Container):
    def __init__(self):
        _Container.__init__(self)
        self.at = audiotools.MP3Audio
class MP2Container(_Container):
    def __init__(self):
        _Container.__init__(self)
        self.at = audiotools.MP2Audio
class VorbisContainer(_Container):
    def __init__(self):
        _Container.__init__(self)
        self.at = audiotools.VorbisAudio
class WaveContainer(_Container):
    def __init__(self):
        _Container.__init__(self)
        self.at = audiotools.WaveAudio

class TrackMeta():
    def __init__(self):
        self.track_no = 0
        self.duration = 0
        self.name = ""
        self.artist = ""
        self.performer = ""
        self.composer = ""
        self.conductor = ""
        self.isrc = ""
        
        self.year = ""
        self.date = ""
        self.catalog = ""
        self.album_name = ""
        self.album_number = 0
        self.album_total = 0
class Track():
    def __init__(self, track, no):
        self._track = track
        self.no = no
        self.meta = TrackMeta()
class Device():
    def __init__(self, device):
        try:
            self._cd = audiotools.CDDA(device)
            self._cdMeta = self._cd.metadata_lookup()[0]
        except AssertionError:
            raise CannotOpenDevice(device)
        
        self.device = device
        self.tracks = []
    
    def load(self, hconf):
        try:
            self._load(hconf)
        except Exception as e:
            raise CannotLoadDevice(self.device, e)
    
    def _load(self, hconf):
        for i in range(len(self._cd)):
            md = self._cdMeta[i]
            track = Track(self._cd[i+1], i+1)
            
            tm = TrackMeta()
            tm.track_no = md.track_number
            tm.duration = (track._track.end-track._track.start) / 75.0
            tm.name = md.track_name
            tm.artist = md.artist_name
            tm.performer = md.performer_name
            tm.composer = md.composer_name
            tm.conductor = md.conductor_name
            tm.isrc = md.ISRC
            tm.album_name = md.album_name
            tm.year = md.year
            tm.date = md.date
            tm.catalog = md.catalog
            
            if tm.name == None:
                tm.name = u"{} #{}".format(lang(hconf=hconf)["track"], tm.track_no)
            for k in ["artist", "performer", "composer", "conductor", "isrc", "album_name", "year", "date", "catalog"]:
                if eval("tm.{}".format(k)) == None:
                    exec('tm.{} = ""'.format(k))
            
            track.meta = tm
            self.tracks.append( track )

def __example():
    device = Device("/dev/cdrom")
    device.load()
    
    print("ogg")
    VorbisContainer().save(device.tracks[1], "/home/user/test.ogg")
    
    print("mp3")
    MP3Container().save(device.tracks[2], "/home/user/test.mp3")
    
    print("wav")
    WaveContainer().save(device.tracks[3], "/home/user/test.wav")