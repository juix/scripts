#!/usr/bin/env python
# -*- coding: utf-8 -*- 
'''
Authr: João Juíz
'''
from BeautifulSoup import BeautifulSoup as Bsoup
from urlparse import urlparse
import urllib,os,re,urllib2
import subprocess

from webFunctions import _Web
from siteSpecific import MotherlessSpecific as Website
from framework import FileOperations,FW
from database import Database

class MediumNoDB(_Web,FileOperations):
    """
    A favourised item.
    """
        
    def __init__(self,websiteUrl):
        self.websiteUrl=websiteUrl
        self._setId(websiteUrl)
        
    def _setId(self,websiteUrl):
        path = urlparse(self.websiteUrl).path
        base = os.path.basename(path)
        if base != "": self.id=self.safeFilename(base)
        else: self.id=self.safeFilename(path)
        
    def existsAtDestination(self,dest):
        raise Exception("MediumNoDB.existsAtDestination is deprecated!")
        return os.path.exists(os.path.join(dest,self.filename))
        
    def _retrieveProperties(self):
        """
        Load website content and set title, filename, etc.
        """
        self._retrieveProperties=lambda:None

        # TODO:
        # if os.path.exists(os.path.join("html",self.id)): self.websiteContent=fromFile(...); else:
        self.websiteContent = self.get(self.websiteUrl)
        self.relatedWebsite = RelatedWebsite(self.id)
        soup=Bsoup(self.websiteContent)
        self.isLeaf = Website.isLeaf(soup)
        
        if not self.isLeaf: return
        self.isPhoto = Website.isPhoto(soup)
        if self.isPhoto: self.mediaUrl = Website.getPicUrl(soup)
        else: self.mediaUrl = Website.getVideoUrl(soup)
        self.title=Website.getName(soup)
        self._setFilename()
        self.numFaved=Website.getNumFaved(self.websiteContent)
        
    def _setFilename(self):
        filename="%s - %s%s"%(self.title,self.id,self.getExtension(urlparse(self.mediaUrl).path))
        #name=self.title#+self.getExtension(self.mediaUrl)
        self.filename=self.safeFilename(filename,175)
        
    def downloadFinished(self):
        raise Exception("Not Implemented, use existsAtDestination(path)")
        
    def isBeingDownloaded(self):
        return False
        
    def download(self,destination,confdir):
        # Kritischer Abschnitt Start
        self._retrieveProperties()
        if not self.isLeaf: 
            raise NoLeafException(self.websiteUrl)
        filename = os.path.join(destination,self.filename)
        filename_temp = filename+".part"
        if self.isPhoto:
            urllib.urlretrieve(self.mediaUrl, filename_temp)
        else:
            # is video
            print "\tvideo:", self.mediaUrl
            subprocess.check_call(["/usr/bin/wget","-c","--user-agent=Mozilla 5.0","-O",filename_temp,self.mediaUrl])
            # returncode == 0. download completed successfully
            #urllib.urlretrieve(self.mediaUrl, os.path.join(destination,"by-id",self.id))
            
            #ydl = YoutubeDL({'out})
            #ydl.download([self.websiteUrl])
        os.rename(filename_temp, filename)
        self.saveHtmlFile(str(confdir))
        # Kritischer Abschnitt Ende
        
    def saveHtmlFile(self,destination):
        self._retrieveProperties()
        self.mkdirq(os.path.join(destination,"html"))
        with open(os.path.join(destination,"html",self.id),"w") as f:
            f.write(self.websiteContent)
        with open(os.path.join(destination,"html",self.relatedWebsite.id),"w") as f:
            f.write(str(self.relatedWebsite))
        

class Medium(MediumNoDB):
    """
    Use this to enable parallel use and skip downloaded files.
    Do Database.load() before initialising this.
    """
    def __init__(self,websiteUrl):
        super(Medium,self).__init__(websiteUrl)

    def download(self, dest, confdir, force=False):
        if (not force) and (self.downloadFinished() or self.isBeingDownloaded()): 
            FW.error("%s already downloaded."%self.id)
            return
        Database.notify_startDownload(self.id)
        super(Medium,self).download(dest, confdir)
        Database.notify_finishedDownload(self.id)

    def downloadFinished(self):
        return Database.hasId(self.id)
        
    def isBeingDownloaded(self):
        return Database.isDownloading(self.id)

class RelatedWebsite(_Web):
    """
    Website with the content “also favourised” of an item
    """
    def __init__(self,id):
        self.id="H"+id
        self.url=os.path.join("http://motherless.com",self.id)
        try:
            self.websiteContent = self.get(self.url)
        except urllib2.HTTPError: 
            self.websiteContent = ""
        
    def __str__(self): return self.websiteContent
    
class NoLeafException(Exception):
    def __init__(self, value): self.value=value
    def __str__(self): return "Error: The element %s does not contain media."%self.value
    
    
