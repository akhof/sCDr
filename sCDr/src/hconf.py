#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os as _os, sys as _sys
from datetime import datetime as _dt

__VERSION__ = "0.1"
__LICENSE__ = "MIT"
__USAGE__ = """
hconf is a little module to manage simple configurations I made for myself. Maybe you need this...

Classes:
    Hconf
        + __init__(fieldDefinition, path, serialer=Serialer)
        + existPath()                                                     return True if the path exists
        + load()                                                          Loads the hconf
        + save()                                                          Saves the hconf
        + SET(key, value)                                                 Sets the field -key- to the value -value-
        + GET(key)                                                        Returns the value of the field -key-
        + GET_ALL()                                                       Returns a dict with all fields {key:value}
        (+ invalidVersionFound(myVersion, foundVersion, foundValues)      This function is called if while loading the Hconf a version found with an other version-code (normaly this func. im empty. You have to override in an own class)
                                                                              -myVersion- is the excepted version -foundVersion- is the in the Hconf found version -foundValues- are the vaues found in the Hconf
                                                                              if this function returns True the pöd hconf is converted successfull. You have to save the hconf if you change sth. with self.SET()
    FieldDefinition
        + __init__(version=1)
        + addField(field)                                                 adds a field to the Hconf-FileDefinition
    
    Field
        + __init__(key, default=None, types=[])                           the types-list contains all datatypes this field can have. If there's no entry all types are excepted.
    
    Serial
        + _serial(o)                                                      this function has to be overridden. -o- contains a dict which hs to be 'converted' to a string which has to be returned
        + _unserial(o)                                                    this function has to be overridden. -o- contains a 'converted' string which has to be 'unconverted' to a dict which has to be returned
    
    cPickleSerial  <- Serial                                              this class is a serialer which uses cPickle and not pickle. This is much faster if you want to convert big or many data


Exceptions:
    _base_                                                                all exceptions contains the functions of this class
        + getTraceback()
        + getMsg()

    CannotSaveHconf  <- _base_                                            this exception is raised if there was an error while saveing Hconf
    CannotLoadHconf  <- _base_                                            this exception is raised if there was an error while loading Hconf
    InvalidKey       <- _base_, __builtin__.KeyError                      this exception is raised if an invalid key was tried to set or get
                                                                              you can catch this with the built-in KeyError
    InvalidFieldType <- _base_, __builtin__.TypeError                     this exception is raised if you tried to give an field an invalid value
                                                                              you can catch this exception with the built-in TypeError
"""

_now = _dt.now

class _exc(Exception):
    def __init__(self, msg="", tb=None):
        Exception.__init__(self)
        self._msg = msg
        self._tb = tb
    def _unicode(self):
        return u"\n\n{}{}\n\n".format(self._msg if len(self._msg) > 0 else "## no message ##", "("+self._tb+")" if self._tb != None else "")
    def __str__(self):
        if _sys.version[0] == "2": #Python 2
            return self._unicode().encode("utf-8")
        else: #Python 3
            return self._unicode()
    def __unicode__(self):
        return self._unicode()
    def getTraceback(self):
        return self._tb
    def getMsg(self):
        return self._msg

class CannotSaveHconf(_exc):
    def __init__(self, tb):
        _exc.__init__(self, tb=tb)
class CannotLoadHconf(_exc):
    def __init__(self, tb):
        _exc.__init__(self, tb=tb)
class InvalidKey(_exc, KeyError):
    def __init__(self, key):
        _exc.__init__(self, msg=u"Invalid key: " + key)
        KeyError.__init__(self)
class InvalidFieldType(_exc, TypeError):
    def __init__(self, getType, needTypes):
        oneof = ""
        for nt in needTypes:
            oneof += str(nt) + ", "
        _exc.__init__(self, msg=u"Invalid type: get {} but need {}{}".format(getType, "one of " if len(needTypes) > 1 else "", "" if len(oneof) == 0 else oneof[:-2]))
        TypeError.__init__(self)

class Serialer():
    def __init__(self, fieldDefinition=None, values=None):
        self.fieldDefinition = fieldDefinition
        self.values = values
    def serial(self):
        obj = {}
        obj["fielddef"] = self.fieldDefinition
        obj["values"] = self.values
        return self._serial(obj)
    def unserial(self, s):
        obj = self._unserial(s)
        self.fieldDefinition = obj["fielddef"]
        self.values = obj["values"]

    def _serial(self, o):
        import pickle, base64
        return base64.b64encode( pickle.dumps( o ) )
    def _unserial(self, o):
        import pickle, base64
        return pickle.loads( base64.b64decode( o ) )
class cPickleSerialer(Serialer):
    def _serial(self, o):
        import cPickle, base64
        return base64.b64encode( cPickle.dumps( o ) )
    def _unserial(self, o):
        import cPickle, base64
        return cPickle.loads( base64.b64decode( o ) )

class Hconf():
    def __init__(self, fieldDefinition, path, serialer=Serialer):
        self._fieldDefinition = fieldDefinition
        self._path = path
        self._serialer = serialer

        self._datetimeOfCreate = None
        self._lastEdit = None

        self._values = {}

        for field in self._fieldDefinition.fields:
            self._values[field._key] = field._default

    def existPath(self):
        return _os.path.isfile(self.path)
    def existHconf(self):
        if not self.existPath():
            return False
        try:
            Hconf(self._fieldDefinition, self._path, self._serialer).load()
        except:
            return False
        return True
    
    def load(self):
        try:
            serialer = self._serialer()
            
            with open(self._path, "rb") as f:
                ctn = f.read()
            serialer.unserial(ctn)
            fieldDefinition = serialer.fieldDefinition
            values = serialer.values
            if fieldDefinition._version != self._fieldDefinition._version:
                if self.invalidVersionFound(self._fieldDefinition._version, fieldDefinition._version, values):
                    self.load()
            else:
                self._fieldDefinition = fieldDefinition
                self._values = values
        except Exception as e:
            raise CannotLoadHconf(e)
    def save(self):
        if not _os.path.isfile(self._path):
            self._datetimeOfCreate = _now()
        self._lastEdit = _now()
            
        try:
            ctn = self._serialer(self._fieldDefinition, self._values).serial()
            with open(self._path, "wb") as f:
                f.write(ctn)
        except Exception as e:
            raise CannotSaveHconf(e)

    def SET(self, key, value):
        field = None
        for _field in self._fieldDefinition.fields:
            if _field._key == key:
                field = _field
        if field == None:
            raise KeyError(key)
        if len(field._types)>0 and type(value) not in field._types and value != None:
            raise InvalidFieldType(type(value), field._types)
        self._values[key] = value
    def GET(self, key):
        try:
            return self._values[key]
        except:
            raise KeyError(key)
    def GET_ALL(self):
        return self._values
    
    def invalidVersionFound(self, myVersion, foundVersion, foundValues):
        return False
class Field():
    def __init__(self, key, default=None, types=[]):
        self._key = key
        self._default = default
        self._types = types
class FieldDefinition():
    def __init__(self, version=1):
        self._version = version
        self.fields = []
        
    def addField(self, field):
        self.fields.append(field)


def _example():
    import pickle, datetime

    # Here the fields of th Hconf are defined
    class myFieldDefinition(FieldDefinition):
        def __init__(self):
            FieldDefinition.__init__(self, 2)
            self.addField( Field("lang", "en", [str]) ) # the field 'lang' with the default-value 'en' and the type 'str'
            self.addField( Field("lastlogins", [], [list]) )
            self.addField( Field("username", "", [str]) )
            self.addField( Field("password", "", [str]) )
            self.addField( Field("number", 0, [int, float]) ) # the field 'number' can contains the types 'int' or 'float'
            self.addField( Field("alwaysStart", True, [bool, int]) )
            self.addField( Field("dummy") ) # the field 'dummy' has no default-value (=None) and can contains all types

    # Here an own serialer is defined to serial the Hconf (write to file / load from file)
    class mySerialer(Serialer):
        def _serial(self, o):
            return pickle.dumps( o )
        def _unserial(self, o):
            return pickle.loads( o )

    # Here an own Hconf is defined (only to override the function 'invalidVersionFound'; if you don't want to override this function you can create an instance of Hconf)
    class myHconf(Hconf):
        def invalidVersionFound(self, myVersion, foundVersion, foundValues):
            print("found an invalid version (old:{}, my:{}!".format(foundVersion, myVersion))
            # Try to ocnvert the old version th the new version...
            if foundVersion > 2:
                return False # converting was not successfull, because the version of the existing Hconf-file is to new (version > 2) and you don't know how it is built
            else:
                try:
                    # all values of version 2 has the defaut-values
                    # the version 1 has only the fields "lang", "username" and "pwd". You have to know the FieldDefinition of Version 1. This is not directly defined here.
                    self.SET("lang", foundValues["lang"])
                    self.SET("username", foundValues["username"])
                    self.SET("password", foundValues["pwd"])
                    self.save() #!!!
                    return True #return True means that the convertig was successfull. You have to save the Hconf if you made changes!
                except:
                    return False

    
    ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###


    path = "/home/you/username/any/file"
    action = "save" # 'save' or 'load'
    useDefaultSerialer = False

    if useDefaultSerialer:
        # The built-in converter which uses pickle and base64 to serial the Hconf
        h = Hconf(myFieldDefinition(), path)
    else:
        # The serialer you defined above
        h = Hconf(myFieldDefinition(), path, mySerialer)
    
    if action == "save":
        h.SET("lang", "de")
        h.SET("username", "root")
        h.SET("password", "aNotSoGoodPassword")
        h.SET("lastlogins", [datetime.date(2015, 2, 12), datetime.date(2015, 2, 9), datetime.date(2015, 9, 4)])
        h.SET("number", 123.456)
        h.SET("alwaysStart", False)
        h.save()
    else:
        h.load()
        print(h.GET_ALL())


if __name__ == "__main__":
    print("Running hconf-example...")
    _example()