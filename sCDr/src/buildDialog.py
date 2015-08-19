#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx, time, thread, os, random, shutil, wave, audiotools
import core, lang

def secsToTime(secs):
    m = str(int(secs // 60))
    s = str(int(int(secs) - (60 * int(m))))
    return "{}{}:{}{}".format("0" if len(m) == 1 else "", m, "0" if len(s) == 1 else "", s)

class buildDialog(wx.Dialog):
    def __init__(self, parent, *args, **kwds):
        self.parent = parent
        wx.Dialog.__init__(self, parent, *args, **kwds)
        
        self.lang = lang.lang(hconf=self.parent.hconf)
        self.__init_wx()
        
        tc = 0
        for i in range(self.parent.trackList.GetItemCount()):
            if self.parent.trackList.IsChecked(i): tc += 1
        
        self.finished = False
        self.progress = 0
        self.starttime = 0
        self.prepareFinished = False
        self.readtracksFinished = False
        self.connecttracksFinished = False
        self.laststepsFinished = False
        self.doConnect = parent.radio_onefile.GetValue()
        self.tracksCount = tc
        self.tracksFinished = 0
        
        self.restSecounds = 0 #so viele Sekunden muessen insgesammt noch ausgelesen werden
        self.saved_time = 0
        self.saved_secs = 0 #so viele Sekunden wurden in der Zeit saved_time gespeichert
        
        self.resttime = 0
        self.resttimeAtTime = 0 #zu diesem zeitpunkt wurde die resttime gesetzt 
        self.canceld = False
        self.error = False
        self.traceback = None
        self.ext = {0:"mp3", 1:"mp2", 2:"wav", 3:"ogg", 4:"flac"}[parent.choice_container.GetSelection()] 
        
        for i in range(self.tracksCount):
            self.restSecounds += self.parent.device.tracks[i].meta.duration
        
    def __init_wx(self):
        self.label_prepare = wx.StaticText(self, wx.ID_ANY, self.lang["prepare"])
        self.label_v_prepare = wx.StaticText(self, wx.ID_ANY, self.lang["elapsed"])
        self.label_tracks = wx.StaticText(self, wx.ID_ANY, self.lang["reading_tracks"])
        self.label_v_tracks = wx.StaticText(self, wx.ID_ANY, "0 / 0")
        self.label_connect = wx.StaticText(self, wx.ID_ANY, self.lang["connect_tracks_build"])
        self.label_v_connect = wx.StaticText(self, wx.ID_ANY, self.lang["skipped"])
        self.label_last = wx.StaticText(self, wx.ID_ANY, self.lang["final_steps"])
        self.label_v_last = wx.StaticText(self, wx.ID_ANY, self.lang["elapsed"])
        self.sl1 = wx.StaticLine(self, wx.ID_ANY, style=wx.EXPAND)
        self.label_time1 = wx.StaticText(self, wx.ID_ANY, self.lang["elapsed_time"])
        self.label_v_time1 = wx.StaticText(self, wx.ID_ANY, "00:00")
        self.label_time2 = wx.StaticText(self, wx.ID_ANY, self.lang["pending_time"])
        self.label_v_time2 = wx.StaticText(self, wx.ID_ANY, "00:00")
        self.gauge = wx.Gauge(self, wx.ID_ANY, 100, style=wx.GA_HORIZONTAL)

        self.SetTitle(self.lang["dialog_title"])
        self.SetBackgroundColour(wx.Colour(102, 102, 102))
        self.label_prepare.SetBackgroundColour(wx.Colour(102, 102, 102))
        self.label_prepare.SetForegroundColour(wx.Colour(174, 255, 0))
        self.label_prepare.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_v_prepare.SetBackgroundColour(wx.Colour(102, 102, 102))
        self.label_v_prepare.SetForegroundColour(wx.Colour(255, 108, 0))
        self.label_v_prepare.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.label_tracks.SetBackgroundColour(wx.Colour(102, 102, 102))
        self.label_tracks.SetForegroundColour(wx.Colour(174, 255, 0))
        self.label_tracks.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_v_tracks.SetBackgroundColour(wx.Colour(102, 102, 102))
        self.label_v_tracks.SetForegroundColour(wx.Colour(255, 108, 0))
        self.label_v_tracks.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.label_connect.SetBackgroundColour(wx.Colour(102, 102, 102))
        self.label_connect.SetForegroundColour(wx.Colour(174, 255, 0))
        self.label_connect.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_v_connect.SetBackgroundColour(wx.Colour(102, 102, 102))
        self.label_v_connect.SetForegroundColour(wx.Colour(255, 108, 0))
        self.label_v_connect.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.label_last.SetBackgroundColour(wx.Colour(102, 102, 102))
        self.label_last.SetForegroundColour(wx.Colour(174, 255, 0))
        self.label_last.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_v_last.SetBackgroundColour(wx.Colour(102, 102, 102))
        self.label_v_last.SetForegroundColour(wx.Colour(255, 108, 0))
        self.label_v_last.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.label_time1.SetBackgroundColour(wx.Colour(102, 102, 102))
        self.label_time1.SetForegroundColour(wx.Colour(174, 255, 0))
        self.label_time1.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_v_time1.SetBackgroundColour(wx.Colour(102, 102, 102))
        self.label_v_time1.SetForegroundColour(wx.Colour(255, 108, 0))
        self.label_v_time1.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.label_time2.SetBackgroundColour(wx.Colour(102, 102, 102))
        self.label_time2.SetForegroundColour(wx.Colour(174, 255, 0))
        self.label_time2.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_v_time2.SetBackgroundColour(wx.Colour(102, 102, 102))
        self.label_v_time2.SetForegroundColour(wx.Colour(255, 108, 0))
        self.label_v_time2.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        
        sizer_1 = wx.FlexGridSizer(3, 3, 0, 0)
        sizer_2 = wx.FlexGridSizer(3, 1, 10, 0)
        sizer_4 = wx.FlexGridSizer(2, 1, 10, 0)
        sizer_5 = wx.FlexGridSizer(1, 5, 0, 10)
        sizer_3 = wx.FlexGridSizer(4, 2, 10, 10)
        sizer_1.Add((20, 20), 0, 0, 0)
        sizer_1.Add((20, 20), 0, 0, 0)
        sizer_1.Add((20, 20), 0, 0, 0)
        sizer_1.Add((20, 20), 0, 0, 0)
        sizer_3.Add(self.label_prepare, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_3.Add(self.label_v_prepare, 0, 0, 0)
        sizer_3.Add(self.label_tracks, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_3.Add(self.label_v_tracks, 0, 0, 0)
        sizer_3.Add(self.label_connect, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_3.Add(self.label_v_connect, 0, 0, 0)
        sizer_3.Add(self.label_last, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_3.Add(self.label_v_last, 0, 0, 0)
        sizer_2.Add(sizer_3, 1, wx.EXPAND, 0)
        sizer_2.Add(self.sl1, 0, wx.EXPAND, 0)
        sizer_5.Add(self.label_time1, 0, 0, 0)
        sizer_5.Add(self.label_v_time1, 0, 0, 0)
        sizer_5.Add((20, 20), 0, 0, 0)
        sizer_5.Add(self.label_time2, 0, 0, 0)
        sizer_5.Add(self.label_v_time2, 0, 0, 0)
        sizer_5.AddGrowableCol(0)
        sizer_5.AddGrowableCol(3)
        sizer_4.Add(sizer_5, 1, wx.EXPAND, 0)
        sizer_4.Add(self.gauge, 0, wx.EXPAND, 0)
        sizer_4.AddGrowableCol(0)
        sizer_2.Add(sizer_4, 1, wx.EXPAND, 0)
        sizer_2.AddGrowableCol(0)
        sizer_1.Add(sizer_2, 1, wx.EXPAND, 0)
        sizer_1.Add((20, 20), 0, 0, 0)
        sizer_1.Add((20, 20), 0, 0, 0)
        sizer_1.Add((20, 20), 0, 0, 0)
        sizer_1.Add((20, 20), 0, 0, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        sizer_1.AddGrowableRow(1)
        sizer_1.AddGrowableCol(1)
        self.Layout()
        
        self.Bind(wx.EVT_CLOSE, self.close)
        
    def close(self, event, askForClosing=True):
        if (not self.finished) and askForClosing:
            if not wx.MessageDialog(self, self.lang["ask_close"], self.lang["close_title"], wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION).ShowModal() == wx.ID_YES:
                return
        self.canceld = True
        for _ in range(2):
            wx.CallAfter(self.parent.loadDisk, None)
            time.sleep(0.1)
        self.EndModal(1)
    
    def startBuildInThread(self):
        for o in [self.label_connect, self.label_v_connect]:
            o.Enable(self.doConnect)
        
        self.starttime = time.time()
        thread.start_new(self._TH_checkError, ())
        thread.start_new(self._TH_reloadDisplay, ())
        thread.start_new(self._TH_build, ())
        
        self.ShowModal()
        
    def _TH_build(self):
        try:
            self._TH_do_build()
        except Exception as e:
            self.error = True
            self.traceback = e
    def _TH_do_build(self):
        class AbortException(Exception): pass
        
        time.sleep(0.5)
        
        try:
            ## VORBEREITUNGEN
            if self.canceld or self.error: raise AbortException()
            
            _id = ""
            for _ in range(20): _id += hex(random.randint(16, 255))[2:]
            tmp = os.path.join(self.parent.combo_temp.GetValue(), "cdda-{}".format(_id))
            out = self.parent.combo_out.GetValue()
            device = self.parent.device
            
            if os.path.isdir(tmp):
                print(u"Remove dir '{}'".format(tmp))
                shutil.rmtree(tmp)
            print(u"Creating dir '{}'".format(tmp))
            os.mkdir(tmp)
            if not os.path.isdir(out):
                print(u"Create dir '{}'".format(out))
                os.mkdir(out)
            self.prepareFinished = True
            
            ## Tracks auslesen
            for i in range(self.parent.trackList.GetItemCount()):
                if self.canceld or self.error: raise AbortException()
                
                if not self.parent.trackList.IsChecked(i):
                    continue
                st = time.time()
                
                track = device.tracks[i]
                if self.doConnect:
                    filename = u"trackno{}.wav".format(track.no)
                else:
                    filename = u"{album} - {trackno} - {title}.{ext}".format(album=track.meta.album_name,
                                                                         trackno=track.no,
                                                                         title=track.meta.name,
                                                                         ext=self.ext)
                path = os.path.join(tmp, filename)
                
                print(u"Writing Track #{} to '{}'".format(track.no, path))
                container = {0:core.MP3Container, 1:core.MP2Container,
                             2:core.WaveContainer , 3:core.VorbisContainer,
                             4:core.FlacContainer}[self.parent.choice_container.GetSelection()]()
                if self.doConnect:
                    container = core.WaveContainer()
                container.save(track, path)
                
                self.saved_time += time.time()-st
                self.saved_secs = track.meta.duration
                self.restSecounds -= track.meta.duration
                
                self.resttime = self.restSecounds * (self.saved_time / self.saved_secs) + (int(self.doConnect)*15*self.tracksCount)
                self.resttimeAtTime = time.time()
                
                self.tracksFinished += 1
            self.readtracksFinished = True
            
            ## Zusammenschneiden der Tracks:
            if self.doConnect:
                self.resttime = 15*self.tracksCount #geraten da mir im Moment nichts besseres einfällt...
                self.resttimeAtTime = time.time()
                
                if self.canceld: return
                print("Connecting to one file...")
                data = []
                filesToDelete = []
                for fname in sorted(os.listdir(tmp)):
                    if self.canceld or self.error: raise AbortException()
                    
                    path = os.path.join(tmp, fname)
                    filesToDelete.append(path)
                    print(u"Read '{}'".format(path))
                    f = wave.open(path, "rb")
                    data.append([f.getparams(), f.readframes(f.getnframes())])
                    f.close()
                
                outpathFilename = u"{interpret} - {album}".format(interpret=device.tracks[0].meta.artist,
                                                                album=device.tracks[0].meta.album_name)
                outpath = os.path.join(tmp, outpathFilename+".wav")
                print(u"Saving all files in '{0}'".format(outpath))
                output = wave.open(outpath, 'wb')
                output.setparams(data[0][0])
                for item in data:
                    output.writeframes(item[1])
                output.close()
                
                if self.canceld or self.error: raise AbortException()
                
                if self.ext != "wav":
                    print("Convert connected file...")
                    
                    cont =  {0:audiotools.MP3Audio, 1:audiotools.MP2Audio,
                             2:audiotools.WaveAudio, 3:audiotools.VorbisAudio,
                             4:audiotools.FlacAudio}[self.parent.choice_container.GetSelection()]
                    conOutPath = os.path.join(tmp, outpathFilename+"."+self.ext)
                    audiotools.open(outpath).convert(conOutPath, cont)
                else:
                    conOutPath = outpath
                
                print("Delete old files...")
                for filename in os.listdir(tmp):
                    path = os.path.join(tmp, filename)
                    if path == conOutPath: continue
                    os.remove(path)
                
                self.connecttracksFinished = True
            
            ## Finale Schritte
            print(u"Copy files from '{}' to '{}'".format(tmp, out))
            for f in os.listdir(tmp):
                shutil.copy(os.path.join(tmp, f), out)
            
            print(u"Delete dir '{}'".format(tmp))
            shutil.rmtree(tmp)
            self.laststepsFinished = True
            self.finished = True
            
            wx.CallAfter(self.on_finished)
        except AbortException:
            pass
        finally:
            if os.path.exists(tmp):
                print(u"Delete dir '{}'".format(tmp))
                shutil.rmtree(tmp)
        
    def on_finished(self):
        wx.MessageDialog(self, self.lang["success"], "", wx.ICON_INFORMATION|wx.OK).ShowModal()
    def on_error(self):
        wx.MessageDialog(self, self.error["error"].format(self.traceback), "", wx.ICON_ERROR|wx.OK).ShowModal()
        self.canceld = True
        self.close(None, False)
    
    def _TH_checkError(self):
        while (not self.finished) and (not self.canceld):
            if self.error:
                wx.CallAfter(self.on_error)
                break
            time.sleep(0.5)
    def _TH_reloadDisplay(self):
        def send():
            try:
                oneStep = 1.0/float((2 + self.tracksCount + int(self.doConnect)))
                self.progress = 100 * (float(int(self.prepareFinished) + int(self.connecttracksFinished)
                                       + self.tracksFinished + int(self.laststepsFinished)) * oneStep)
                
                txtVorbereitungen = self.lang["finished"] if self.prepareFinished else self.lang["elapsed"]
                txtTracks = "{} / {}".format(self.tracksFinished, self.tracksCount)
                txtConnect = "" if not self.doConnect else (self.lang["finished"] if self.connecttracksFinished else self.lang["elapsed"])
                txtLaststeps = self.lang["finished"] if self.laststepsFinished else self.lang["elapsed"]
                txtTime = secsToTime(time.time()-self.starttime)
                
                if self.finished or self.canceld:
                    txtRestTime = "00:00"
                elif self.resttimeAtTime == 0 and self.resttime == 0:
                    txtRestTime = "???"
                else:
                    secs = self.resttime-(time.time()-self.resttimeAtTime)
                    if secs < 0:
                        txtRestTime = "???"
                    else:
                        txtRestTime = secsToTime(secs)
                
                wx.CallAfter(self.setStatus,
                             txtVorbereitungen, txtTracks, txtConnect, txtLaststeps, txtTime, txtRestTime, self.progress)
            except:
                pass
        
        while (not self.finished) and (not self.canceld) and (not self.error):
            send()
            time.sleep(1)
        send()
    
    def setStatus(self, txtVorbereitungen, txtTracks, txtConnect, txtLaststeps, txtTime, txtRestTime, progress):
        self.label_v_prepare.SetLabel(txtVorbereitungen)
        self.label_v_tracks.SetLabel(txtTracks)
        self.label_v_connect.SetLabel(txtConnect)
        self.label_v_last.SetLabel(txtLaststeps)
        self.label_v_time1.SetLabel(txtTime)
        self.label_v_time2.SetLabel(txtRestTime)
        self.gauge.SetValue(progress)
    