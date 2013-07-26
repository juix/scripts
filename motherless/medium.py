#!/usr/bin/env python
# -*- coding: utf-8 -*- 
'''
Authr: João Juíz
'''
from webFunctions import _Web
from siteSpecific import MotherlessSpecific as Website
from framework import FileOperations
from BeautifulSoup import BeautifulSoup as Bsoup
from urlparse import urlparse
import urllib,os
from youtube_dl import YoutubeDL
import subprocess

class Medium(_Web,FileOperations):
    """
    A favourised item.
    """
    #def __new__(cls,url):
        #soup=Bsoup(self.get(url))
        
    def __init__(self,websiteUrl):
        self.websiteUrl=websiteUrl
        self._setId(websiteUrl)
        
    def _setId(self,websiteUrl):
        path = urlparse(self.websiteUrl).path
        base = os.path.basename(path)
        if base != "": self.id=self.safeFilename(base)
        else: self.id=self.safeFilename(path)
        
    def existsAtDestination(self,dest):
        return os.path.exists(os.path.join(dest,"by-id",self.id))
        
    def __call__(self):
        soup=Bsoup(self.get(self.websiteUrl))
        self.isPhoto = Website.isPhoto(soup)
        if self.isPhoto: self.mediaUrl = Website.getPicUrl(soup)
        else: self.mediaUrl = Website.getVideoUrl(soup)
        self.title=Website.getName(soup)
        self._setFilename()
        
    def _setFilename(self):
        filename="%s - %s%s"%(self.title,self.id,self.getExtension(self.mediaUrl))
        #name=self.title#+self.getExtension(self.mediaUrl)
        self.filename=self.safeFilename(filename)
        
    def download(self,destination):
        self.mkdirq(os.path.join(destination,"by-id"))
        if self.isPhoto:
            urllib.urlretrieve(self.mediaUrl, os.path.join(destination,"by-id",self.id))
        else:
            # is video
            print "\tvideo:", self.mediaUrl
            subprocess.check_call(["/usr/bin/wget","--user-agent=Mozilla 5.0","-O",os.path.join(destination,"by-id",self.id),self.mediaUrl])
            #urllib.urlretrieve(self.mediaUrl, os.path.join(destination,"by-id",self.id))
            
            #ydl = YoutubeDL({'out})
            #ydl.download([self.websiteUrl])
        self.createSymlink(destination)
        
    def createSymlink(self,destination):
        self.mkdirq(os.path.join(destination,"by-name"))
        #self.mkdirq(os.path.join(destination,"by-id-and-name"))
        try:
            os.symlink(os.path.join("../by-id/",self.id), os.path.join(destination,"by-name",self.filename))
        except OSError: pass
        #try:
        #    os.symlink(os.path.join("../by-id/",self.id), os.path.join(destination,"by-id-and-name",self.id+" "+self.filename))
        #except OSError: pass

