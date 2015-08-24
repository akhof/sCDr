#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx, os, sys, platform, tempfile, thread, time, subprocess
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin
import hconf, core, buildDialog, lang, about

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)

def getDevices():
    dev = []
    try:
        print("Try to detect devices...")
        for line in subprocess.check_output(["lsscsi"]).split("\n"):
            if "cd/dvd" in line or "cd" in line:
                params = line.split(" ")
                device = params[len(params)-2]
                print(u"\t{}".format(device))
                dev.append(device)
    except:
        print("Cannot detect devices...")
    return dev

class MainFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        
        self.action = 1 #show option #1 (=1) or an other option (!=1)
        self.groups = {}
        self.hconf = None
        self.userHomePath = ""
        self.device = None
        
        self.lang = None
        self.lastIsos = None
        self.lastTmps = None
        self.lastOuts = None
        
        self.__init_hconf()
        self.__load_hconf()
        self.__init_lang()
        
        self.__init_wx()
    
    def __init_lang(self):
        self.lang = lang.lang(hconf=self.hconf)
    
    def __init_hconf(self):
        if platform.system() == "Linux":
            uhome = os.environ['HOME']
        elif platform.system() == "Windows":
            uhome = os.getenv("USERPROFILE")
        else:
            self.showError(u"Unknown system: '{}'".format(platform.system()), exit=True)
        path = os.path.join(uhome, ".scdr_hconf")
        self.userHomePath = uhome
        
        print(u"Init hconf with path '{}'".format(path))
        
        field = hconf.Field
        fields = hconf.FieldDefinition()
        fields.addField( field("lang", "en", [str,]) )
        fields.addField( field("lastIsos", [], [list,]) )
        fields.addField( field("lastTmps", [], [list,]) )
        fields.addField( field("lastOuts", [], [list,]) )
        self.hconf = hconf.Hconf(fields, path)
        if not self.hconf.existHconf():
            print("Saving hconf first time...")
            self.hconf.save()
    def __load_hconf(self):
        self.hconf.load()
        self.langcode = self.hconf.GET("lang")
        self.lastIsos = self.hconf.GET("lastIsos")
        self.lastTmps = self.hconf.GET("lastTmps")
        self.lastOuts = self.hconf.GET("lastOuts")
        
        if len(self.lastIsos) > 8: self.lastIsos = self.lastIsos[:8]
        if len(self.lastOuts) > 8: self.lastOuts = self.lastOuts[:8]
        if len(self.lastTmps) > 8: self.lastTmps = self.lastTmps[:8]
    
    def __init_wx(self):
        self.label_step1 = wx.StaticText(self, wx.ID_ANY, self.lang["step_1_select_medium"])
        self.radio_device = wx.RadioButton(self, wx.ID_ANY, self.lang["physical_device"])
        self.combo_device = wx.ComboBox(self, wx.ID_ANY, choices=getDevices(), style=wx.CB_DROPDOWN)
        self.radio_iso = wx.RadioButton(self, wx.ID_ANY, self.lang["iso_image"])
        self.combo_iso = wx.ComboBox(self, wx.ID_ANY, choices=self.lastIsos, style=wx.CB_DROPDOWN)
        self.button_iso_open = wx.Button(self, wx.ID_ANY, self.lang["open"])
        self.sl1 = wx.StaticLine(self, wx.ID_ANY, style=wx.EXPAND)
        self.label_step2 = wx.StaticText(self, wx.ID_ANY, self.lang["step_2_select_tracks"])
        self.button_loadDisk = wx.Button(self, wx.ID_ANY, self.lang["read_tracks"])
        
        self.trackList = CheckListCtrl(self)
        self.trackList.InsertColumn(0, self.lang["no"], width=50)
        self.trackList.InsertColumn(1, self.lang["list_title"])
        self.trackList.InsertColumn(2, self.lang["album"])
        self.trackList.InsertColumn(3, self.lang["interpreter"])
        self.trackList.InsertColumn(4, self.lang["duration"])
        self.trackList.InsertColumn(5, self.lang["year"])

        self.sl2 = wx.StaticLine(self, wx.ID_ANY, style=wx.EXPAND)
        self.label_step3 = wx.StaticText(self, wx.ID_ANY, self.lang["step_3_options"])
        self.label_temp = wx.StaticText(self, wx.ID_ANY, self.lang["temp_path"])
        self.combo_temp = wx.ComboBox(self, wx.ID_ANY, choices=self.lastTmps, style=wx.CB_DROPDOWN)
        self.button_temp_open = wx.Button(self, wx.ID_ANY, self.lang["open"])
        self.label_out = wx.StaticText(self, wx.ID_ANY, self.lang["out_path"])
        self.combo_out = wx.ComboBox(self, wx.ID_ANY, choices=self.lastOuts, style=wx.CB_DROPDOWN)
        self.button_out_open = wx.Button(self, wx.ID_ANY, self.lang["open"])
        self.label_container = wx.StaticText(self, wx.ID_ANY, self.lang["container"])
        self.choice_container = wx.Choice(self, wx.ID_ANY, choices=["MP3 (.mp3)", "MP2 (.mp2)", "Wave (.wav)", "Vorbis (.ogg)", "flac (.flac)"])
        self.radio_onefile = wx.CheckBox(self, wx.ID_ANY, self.lang["connect_tracks"])
        self.button_start = wx.Button(self, wx.ID_ANY, self.lang["start"])
        
        self.combo_temp.SetValue(tempfile.gettempdir())
        self.combo_out.SetValue(os.path.join(self.userHomePath, "CD"))
        
        self.menubar = wx.MenuBar()
        self.file = wx.Menu()
        self.close = wx.MenuItem(self.file, wx.NewId(), self.lang["close"], "", wx.ITEM_NORMAL)
        self.file.AppendItem(self.close)
        self.menubar.Append(self.file, self.lang["file"])
        self.language = wx.Menu()
        self.german = wx.MenuItem(self.language, wx.NewId(), "Deutsch", "", wx.ITEM_RADIO)
        self.language.AppendItem(self.german)
        self.english = wx.MenuItem(self.language, wx.NewId(), "English", "", wx.ITEM_RADIO)
        self.language.AppendItem(self.english)
        self.menubar.Append(self.language, "Language")
        self.about = wx.Menu()
        self.ueber = wx.MenuItem(self.about, wx.NewId(), self.lang["about"], "", wx.ITEM_NORMAL)
        self.about.AppendItem(self.ueber)
        self.menubar.Append(self.about, self.lang["about"])
        self.SetMenuBar(self.menubar)

        self.german.Check(self.langcode == "de")
        self.english.Check(self.langcode == "en")

        self.__set_properties()
        self.__do_layout()
        self.__init_groups()

        self.showGroup("step1")
        self.showGroup("read")
        self.hideGroup("step2")
        self.hideGroup("step3")
        self.radio_device.SetValue(True)
        self.sel_device(None)

        self.Bind(wx.EVT_RADIOBUTTON, self.sel_device, self.radio_device)
        self.Bind(wx.EVT_RADIOBUTTON, self.sel_iso, self.radio_iso)
        self.Bind(wx.EVT_TEXT, self.changed_medium, self.combo_device)
        self.Bind(wx.EVT_COMBOBOX, self.changed_medium, self.combo_device)
        self.Bind(wx.EVT_TEXT, self.changed_medium, self.combo_iso)
        self.Bind(wx.EVT_COMBOBOX, self.changed_medium, self.combo_iso)
        self.Bind(wx.EVT_BUTTON, self.loadDisk, self.button_loadDisk)
        self.Bind(wx.EVT_BUTTON, self.open_iso, self.button_iso_open)
        self.Bind(wx.EVT_BUTTON, self.open_tmp, self.button_temp_open)
        self.Bind(wx.EVT_BUTTON, self.open_out, self.button_out_open)
        self.Bind(wx.EVT_BUTTON, self.start, self.button_start)
        self.Bind(wx.EVT_MENU, self.exit, self.close)
        self.Bind(wx.EVT_MENU, self.lang_german, self.german)
        self.Bind(wx.EVT_MENU, self.lang_english, self.english)
        self.Bind(wx.EVT_MENU, self.show_ueber, self.ueber)
        self.Bind(wx.EVT_CLOSE, self.exit)
    def __set_properties(self):
        self.SetTitle(self.lang["title"])
        self.SetBackgroundColour(wx.Colour(102, 102, 102))
        self.trackList.SetForegroundColour(wx.Colour(26, 26, 26))
        self.label_step1.SetBackgroundColour(wx.Colour(102, 102, 102))
        self.label_step1.SetForegroundColour(wx.Colour(255, 108, 0))
        self.label_step1.SetFont(wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.radio_device.SetBackgroundColour(wx.Colour(102, 102, 102))
        self.radio_device.SetForegroundColour(wx.Colour(174, 255, 0))
        self.radio_device.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.radio_device.SetValue(1)
        self.combo_device.SetBackgroundColour(wx.Colour(102, 102, 102))
        self.combo_device.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.combo_device.SetSelection(-1)
        self.radio_iso.SetBackgroundColour(wx.Colour(102, 102, 102))
        self.radio_iso.SetForegroundColour(wx.Colour(174, 255, 0))
        self.radio_iso.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.combo_iso.SetBackgroundColour(wx.Colour(102, 102, 102))
        self.combo_iso.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.button_iso_open.SetBackgroundColour(wx.Colour(26, 26, 26))
        self.button_iso_open.SetForegroundColour(wx.Colour(174, 255, 0))
        self.button_iso_open.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.button_loadDisk.SetBackgroundColour(wx.Colour(26, 26, 26))
        self.button_loadDisk.SetForegroundColour(wx.Colour(174, 255, 0))
        self.button_loadDisk.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_step2.SetBackgroundColour(wx.Colour(102, 102, 102))
        self.label_step2.SetForegroundColour(wx.Colour(255, 108, 0))
        self.label_step2.SetFont(wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_step3.SetBackgroundColour(wx.Colour(102, 102, 102))
        self.label_step3.SetForegroundColour(wx.Colour(255, 108, 0))
        self.label_step3.SetFont(wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_temp.SetBackgroundColour(wx.Colour(102, 102, 102))
        self.label_temp.SetForegroundColour(wx.Colour(174, 255, 0))
        self.label_temp.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.combo_temp.SetBackgroundColour(wx.Colour(102, 102, 102))
        self.combo_temp.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.button_temp_open.SetBackgroundColour(wx.Colour(26, 26, 26))
        self.button_temp_open.SetForegroundColour(wx.Colour(174, 255, 0))
        self.button_temp_open.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_out.SetBackgroundColour(wx.Colour(102, 102, 102))
        self.label_out.SetForegroundColour(wx.Colour(174, 255, 0))
        self.label_out.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.combo_out.SetBackgroundColour(wx.Colour(102, 102, 102))
        self.combo_out.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.button_out_open.SetBackgroundColour(wx.Colour(26, 26, 26))
        self.button_out_open.SetForegroundColour(wx.Colour(174, 255, 0))
        self.button_out_open.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_container.SetBackgroundColour(wx.Colour(102, 102, 102))
        self.label_container.SetForegroundColour(wx.Colour(174, 255, 0))
        self.label_container.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.choice_container.SetMinSize((70, 28))
        self.choice_container.SetBackgroundColour(wx.Colour(26, 26, 26))
        self.choice_container.SetForegroundColour(wx.Colour(174, 255, 0))
        self.choice_container.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.choice_container.SetSelection(0)
        self.radio_onefile.SetBackgroundColour(wx.Colour(102, 102, 102))
        self.radio_onefile.SetForegroundColour(wx.Colour(174, 255, 0))
        self.radio_onefile.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.button_start.SetBackgroundColour(wx.Colour(26, 26, 26))
        self.button_start.SetForegroundColour(wx.Colour(255, 108, 0))
        self.button_start.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
    def __do_layout(self):
        sizer_1 = wx.FlexGridSizer(3, 3, 0, 0)
        sizer_2 = wx.FlexGridSizer(8, 1, 10, 0)
        sizer_2a = wx.FlexGridSizer(1, 2, 0, 10)
        sizer_7 = wx.FlexGridSizer(1, 2, 0, 0)
        sizer_8 = wx.FlexGridSizer(2, 1, 10, 0)
        sizer_9 = wx.FlexGridSizer(3, 2, 10, 10)
        sizer_12 = wx.FlexGridSizer(1, 2, 0, 10)
        sizer_11 = wx.FlexGridSizer(1, 2, 0, 10)
        sizer_10 = wx.FlexGridSizer(1, 2, 0, 10)
        sizer_6 = wx.FlexGridSizer(1, 2, 0, 0)
        sizer_3 = wx.FlexGridSizer(1, 2, 0, 0)
        sizer_4 = wx.FlexGridSizer(2, 2, 10, 10)
        sizer_5 = wx.FlexGridSizer(1, 2, 0, 10)
        sizer_1.Add((20, 20), 0, 0, 0)
        sizer_1.Add((20, 20), 0, 0, 0)
        sizer_1.Add((20, 20), 0, 0, 0)
        sizer_1.Add((20, 20), 0, 0, 0)
        sizer_2.Add(self.label_step1, 0, 0, 0)
        sizer_3.Add((20, 20), 0, 0, 0)
        sizer_4.Add(self.radio_device, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_4.Add(self.combo_device, 0, wx.EXPAND, 0)
        sizer_4.Add(self.radio_iso, 0, 0, 0)
        sizer_5.Add(self.combo_iso, 0, wx.EXPAND, 0)
        sizer_5.Add(self.button_iso_open, 0, wx.EXPAND, 0)
        sizer_5.AddGrowableCol(0)
        sizer_4.Add(sizer_5, 1, wx.EXPAND, 0)
        sizer_4.AddGrowableCol(1)
        sizer_3.Add(sizer_4, 1, wx.EXPAND, 0)
        sizer_3.AddGrowableRow(0)
        sizer_3.AddGrowableCol(1)
        sizer_2.Add(sizer_3, 1, wx.EXPAND, 0)
        sizer_2.Add(self.sl1, 0, wx.EXPAND, 0)
        sizer_2a.Add(self.label_step2, 0, 0, 0)
        sizer_2a.Add(self.button_loadDisk, 0, wx.ALIGN_RIGHT, 0)
        sizer_2a.AddGrowableCol(1)
        sizer_2.Add(sizer_2a, 0, wx.EXPAND, 0)
        sizer_2.Add(self.trackList, 0, wx.EXPAND, 0)
        sizer_6.Add((20, 20), 0, 0, 0)
        sizer_6.AddGrowableRow(0)
        sizer_6.AddGrowableCol(1)
        sizer_2.Add(sizer_6, 1, wx.EXPAND, 0)
        sizer_2.Add(self.sl2, 0, wx.EXPAND, 0)
        sizer_2.Add(self.label_step3, 0, 0, 0)
        sizer_7.Add((20, 20), 0, 0, 0)
        sizer_9.Add(self.label_temp, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_10.Add(self.combo_temp, 0, wx.EXPAND, 0)
        sizer_10.Add(self.button_temp_open, 0, wx.EXPAND, 0)
        sizer_10.AddGrowableCol(0)
        sizer_9.Add(sizer_10, 1, wx.EXPAND, 0)
        sizer_9.Add(self.label_out, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_11.Add(self.combo_out, 0, wx.EXPAND, 0)
        sizer_11.Add(self.button_out_open, 0, wx.EXPAND, 0)
        sizer_11.AddGrowableCol(0)
        sizer_9.Add(sizer_11, 1, wx.EXPAND, 0)
        sizer_9.Add(self.label_container, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_12.Add(self.choice_container, 0, 0, 0)
        sizer_12.Add(self.radio_onefile, 0, 0, 0)
        sizer_12.AddGrowableCol(1)
        sizer_9.Add(sizer_12, 1, wx.EXPAND, 0)
        sizer_9.AddGrowableCol(1)
        sizer_8.Add(sizer_9, 1, wx.EXPAND, 0)
        sizer_8.Add(self.button_start, 0, wx.EXPAND, 0)
        sizer_8.AddGrowableCol(0)
        sizer_7.Add(sizer_8, 1, wx.EXPAND, 0)
        sizer_7.AddGrowableRow(0)
        sizer_7.AddGrowableCol(1)
        sizer_2.Add(sizer_7, 1, wx.EXPAND, 0)
        sizer_2.AddGrowableRow(4)
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
        self.SetMinSize(self.GetBestSize())
        self.SetSize(wx.Size(690, 710))
        
    def __init_groups(self):
        self.groups["device"] = [self.combo_device]
        self.groups["iso"] = [self.combo_iso, self.button_iso_open]
        self.groups["read"] = [self.button_loadDisk]
        self.groups["step1"] = [self.radio_device, self.radio_iso, self.button_iso_open,
                                self.combo_device, self.combo_iso, self.label_step1]
        self.groups["step2"] = [self.label_step2, self.trackList]
        self.groups["step3"] = [self.label_step3, self.label_temp, self.label_out, self.label_container,
                                self.combo_temp, self.combo_out, self.choice_container, self.radio_onefile,
                                self.button_temp_open, self.button_out_open, self.button_start]
        self.groups["all"] = [self]
        
    def showGroup(self, name, enable=True):
        for o in self.groups[name]:
            o.Enable(enable)
    def hideGroup(self, name):
        self.showGroup(name, False)

    def loadDisk(self, event):
        self.trackList.DeleteAllItems()
        if self.action == 1:
            self.hideGroup("all")
            
            thread.start_new(self._openDevice, (self.combo_device.GetValue() if self.radio_device.GetValue() else self.combo_iso.GetValue(), ))
            wx.Yield()
        else:
            self.showGroup("step1")
            self.showGroup("read")
            self.hideGroup("step2")
            self.hideGroup("step3")
            self.button_loadDisk.SetLabel(self.lang["read_tracks"])
            self.Layout()
            self.action = 1
            self.device = None
            if self.radio_device.GetValue():
                self.sel_device(None)
            else:
                self.sel_iso(None)
            
        self.Layout()
    def afterLoadDisk(self, e, tracks):
        self.showGroup("all")
    
        if e == None:
            for track in tracks:
                index = self.trackList.InsertStringItem(sys.maxint, track[0])
                self.trackList.SetStringItem(index, 1, track[1])
                self.trackList.SetStringItem(index, 2, track[2])
                self.trackList.SetStringItem(index, 3, track[3])
                self.trackList.SetStringItem(index, 4, track[4])
                self.trackList.SetStringItem(index, 5, track[5])
                self.trackList.CheckItem(index)
            
            self.showGroup("step2")
            self.showGroup("step3")
            self.showGroup("read")
            self.hideGroup("step1")
            self.button_loadDisk.SetLabel(self.lang["change_device"])
            self.Layout()
            self.action = 2
        else:
            self.showError(u"Cannot load tracks! ({})".format(e))

    def _openDevice(self, device):
        e = None
        tracks = []
        try:
            self.device = core.Device(device)
            self.device.load(self.hconf)
            
            no = 0
            for track in self.device.tracks:
                no += 1
                title = track.meta.name
                album = track.meta.album_name
                interpret = track.meta.artist
                duration = core.secsToTime(track.meta.duration)
                year = track.meta.year
                
                tracks.append( (str(no), title, album, interpret, duration, year) )
        except Exception as e:
            pass
        finally:
            wx.CallAfter(self.afterLoadDisk, e, tracks)

    def askQuestion(self, msg="", title=""):
        return wx.MessageDialog(self, msg, title, wx.YES_NO|wx.ICON_QUESTION).ShowModal() == wx.ID_YES
    def showInfo(self, msg="", title=""):
        wx.MessageDialog(self, msg, title, wx.ICON_INFORMATION|wx.OK).ShowModal()
    def showError(self, msg, title="There was an error...", exit=False):
        print(u"There was an error:\n\t{}".format(msg))
        wx.MessageDialog(self, msg, title, wx.ICON_ERROR|wx.OK).ShowModal()
        if exit:
            print("\nExit...")
            sys.exit(1)

    def __dirDialog(self):
        dia = wx.DirDialog(self, "", "", wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST | wx.DD_NEW_DIR_BUTTON)
        if dia.ShowModal() == wx.ID_OK:
            return dia.GetPath()

    def sel_device(self, event):
        self.showGroup("device")
        self.hideGroup("iso")
    def sel_iso(self, event):
        self.hideGroup("device")
        self.showGroup("iso")
        
    def changed_medium(self, event):
        pass

    def open_iso(self, event):
        dia = wx.FileDialog(self, "", "", "", "ISO-Image (*.iso)|*.iso", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dia.ShowModal() == wx.ID_OK:
            path = dia.GetPath()
            self.combo_iso.SetValue(path)
    def open_tmp(self, event):
        p = self.__dirDialog()
        if p != None:
            self.combo_temp.SetValue(p)
    def open_out(self, event):
        p = self.__dirDialog()
        if p != None:
            self.combo_out.SetValue(p)

    def exit(self, event):
        if self.askQuestion(self.lang["ask_close"], self.lang["close_title"]):
            print("Saving new config...")
            self.hconf.SET("lastIsos", self.lastIsos)
            self.hconf.SET("lastTmps", self.lastTmps)
            self.hconf.SET("lastOuts", self.lastOuts)
            self.hconf.save()
            
            self.Hide()
            wx.Yield()
            self.Destroy()
            time.sleep(1)
            sys.exit(0)

    def lang_german(self, event):
        self.__change_lang("de")
    def lang_english(self, event):
        self.__change_lang("en")
    def __change_lang(self, langcode):
        if self.langcode != langcode:
            dia = wx.MessageDialog(self, "You have to reopen the software after changing language. Really change?", "", wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
            if dia.ShowModal() == wx.ID_YES:
                self.hconf.SET("lang", langcode)
                self.hconf.save()
                self.Hide()
                frame = MainFrame(None, wx.ID_ANY, "")
                self.Destroy()
                time.sleep(0.5)
                frame.Show()
    
    def show_ueber(self, event):
        about.show(self.lang)
    
    def start(self, event):
        print("\nStarting ripping CD...")
        ## Speichere letzte Eintraege
        if not self.combo_iso.GetValue() in self.lastIsos:
            self.lastIsos.append( self.combo_iso.GetValue() )
        if not self.combo_temp.GetValue() in self.lastTmps:
            self.lastTmps.append( self.combo_temp.GetValue() )
        if not self.combo_out.GetValue() in self.lastOuts:
            self.lastOuts.append( self.combo_out.GetValue() )
        
        buildDialog.buildDialog(self).startBuildInThread()

###  APP  ##############################################################

class MyApp(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()
        frame = MainFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(frame)
        frame.Show()
        return 1

def start():
    app = MyApp(0)
    app.MainLoop()