#!/usr/bin/env python
# -*- coding: utf-8 -*- 
'''
Authr: João Juíz

This represents the directory to save the database and html files.
'''
import os
from framework import FileOperations

class Confdir(object):
    def __init__(self, path="~/.motherless-dl"):
        self.path=os.path.abspath(os.path.expanduser(path))
        FileOperations.mkdirq(self.path)
        self.database = os.path.join(self.path, "ml.db")
        
    def __str__(self): return self.path
    
