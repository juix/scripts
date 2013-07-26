#!/usr/bin/env python
# -*- coding: utf-8 -*- 
'''
Authr: João Juíz
'''
from BeautifulSoup import BeautifulSoup as Bsoup
from webFunctions import _Web
from siteSpecific import *

class MotherlessSpecificTest(_Web,MotherlessSpecific):
    def __init__(self):
        self.soup=Bsoup(self.get("http://motherless.com/G3CA9F93/20A6782"))
        
    def __call__(self):
        print self.isPhoto(self.soup)
        print self.getName(self.soup)
        print self.getVideoUrl(self.soup)
        
if __name__ == "__main__":
    MotherlessSpecificTest()()

