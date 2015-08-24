#!/usr/bin/env python
# -*- coding: utf-8 -*-
version = "0.1.1"

class lang():
    def __init__(self, langcode=None, hconf=None):
        self.dict = _dict()
        if langcode != None:
            self.langcode = langcode
        elif hconf != None:
            self.langcode = hconf.GET("lang")
        else:
            raise AttributeError()
        if self.langcode not in ["de", "en"]:
            raise Exception()
    
    def __getitem__(self, i):
        try:
            word = eval("self.dict.{}".format(i))
            try:
                return word[self.langcode]
            except:
                return word["en"]
        except:
            return "unknown translation"
    
class _dict():
    def __init__(self):
        ## BASIC
        self.version = {"en":version,
                        "de":version}
        self.open = {"en":"Open",
                     "de":u"Öffnen"}
        self.close = {"en":"Close",
                      "de":u"Schließen"}
        
        
        ## Main-Frame
        self.title = {"en":"sCDr - simple CD ripping",
                      "de":"sCDr - simple CD ripping"}
        self.step_1_select_medium = {"en":"1. Select device",
                                     "de":u"1. Medium auswählen"}
        self.step_2_select_tracks = {"en":"2. Select tracks",
                                     "de":u"2. Tracks auswählen"}
        self.step_3_options = {"en":"3. Options",
                               "de":"3. Optionen"}
        self.physical_device = {"en":"Physical device:",
                                "de":u"Physisches Gerät:"}
        self.iso_image = {"en":"ISO-Image:",
                          "de":"ISO-Image:"}
        self.read_tracks = {"en":"Read tracks",
                           "de":"Tracks einlesen"}
        self.change_device = {"en":"Change device",
                              "de":u"Gerät ändern"}
        self.no = {"en":"No.",
                   "de":"Nr."}
        self.list_title = {"en":"Title",
                           "de":"Titel"}
        self.album = {"en":"Album",
                      "de":"Album"}
        self.interpreter = {"en":"Interpreter",
                            "de":"Interpret"}
        self.duration = {"en":"Duration",
                         "de":u"Länge"}
        self.year = {"en":"Year",
                     "de":"Jahr"}
        self.temp_path = {"en":"Temporary Path:",
                         "de":u"Temporäre Path:"}
        self.out_path = {"en":"Output Path:",
                         "de":"Ausgabe Path:"}
        self.container = {"en":"Container:",
                          "de":"Container:"}
        self.connect_tracks = {"en":"Connect all tracks in one file",
                               "de":"Alle Tracks in eine Datei zusammenschneiden"}
        self.start = {"en":"Start ripping",
                      "de":"Auslesen starten"}
        self.close_title = {"en":"Close?",
                            "de":"Beenden?"}
        self.ask_close = {"en":"Really close?",
                          "de":u"Wirklich schließen?"}
        
        ## Main-Frame-Menu
        self.file = {"en":"File",
                     "de":"Datei"}
        self.about = {"en":"About",
                      "de":u"Über"}
        
        ## Core
        self.track = {"en":"Track",
                     "de":u"Stück"}
        
        
        ## Build-Dialog
        self.prepare = {"en":"Prepare",
                        "de":"Vorbereitungen"}
        self.reading_tracks = {"en":"Reading the tracks",
                               "de":"Auslesen der Tracks"}
        self.connect_tracks_build = {"en":"Connect tracks:",
                                     "de":"Zusammenschneiden der Tracks:"}
        self.final_steps = {"en":"Final steps:",
                            "de":u"Abschließende Schritte:"}
        self.finished = {"en":"finished",
                         "de":u"ausgeführt"}
        self.elapsed = {"en":"elapsed",
                        "de":"ausstehend"}
        self.skipped = {"en":"skipped",
                        "de":u"übersprungen"}
        self.elapsed_time = {"en":"Elapsed time:",
                             "de":"vergangene Zeit:"}
        self.pending_time = {"en":"Pending time:",
                            "de":"ausstehende Zeit:"}
        self.dialog_title = {"en":"Ripping CD...",
                             "de":"CD auslesen..."}
        self.success = {"en":"Success!\nDo you want to open the output path?",
                        "de":u"Erfolgreich!\nSoll das Ausgabe-Verzeichnis geöffnet werden?"}
        self.error = {"en":u"Error ({})",
                      "de":u"Fehler ({})"}
        self.cannot_open_dir = {"en":"Cannot open out-dir!",
                                "de":u"Öffnen des Ausgabe-Verzeichnisses fehlgeschlagen!"}
        
        
        ## About
        self.desc = {"en":"sCDr (=simple CD ripping) is a simple tool for fast ripping audio-CDs. The different tracks on the Cd can be either separately or stored together in different formats. sCDr is using Audiotools.",
                     "de":u"sCDr (=simple CD ripping) ist ein einfaches Tool zum schnellen Auslesen von Audio-CDs. Die einzelnen Tracks der CD können entweder getrennt oder zusammen in verschiedene Formate abgespeichert werden. sCDr nutzt Audiotools."}