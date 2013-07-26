#!/usr/bin/env python
# -*- coding: utf-8 -*- 
'''
Authr: João Juíz
'''
import ConfigParser
import os

class ConfigFile(ConfigParser.ConfigParser,object):
    #def __new__(cls,filename,defaultValues={},**kwargs):
    #    return super(ConfigFile,cls).__new__(cls,defaultValues)
        
    def __init__(self,filename,defaultValues={},**kwargs):
        super(ConfigFile,self).__init__(defaultValues,**kwargs)
        self.filename=os.path.expanduser(filename)
        if os.path.exists(self.filename):
            self.__read()
        else:
            self.__write()
        
    def get(self,key):
        return super(ConfigFile,self).get("DEFAULT",key)
    
    def __write(self):
        with open(self.filename,"w") as configfile:
            self.write(configfile)
            
    def __read(self):
        self.read(self.filename)

