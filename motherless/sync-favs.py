#!/usr/bin/env python
# -*- coding: utf-8 -*- 
'''
Authr: João Juíz
'''
from webFunctions import _Web
import re,os
from urlparse import urljoin
from siteSpecific import MotherlessSpecific as Website
from framework import FileOperations, FW
import argparse
from medium import Medium
from database import Database
from confdir import Confdir

class Main(object):
    def __init__(self):
        pass
    
    def argparser(self):
        parser = argparse.ArgumentParser(description='Sync motherless.com favourites to local directory')
        parser.add_argument("-u",'--username', type=str, required=True, help='Sync favourites of this user')
        parser.add_argument("-o",'--destination', type=str, default=".", help='Save files here, default: ./')
        parser.add_argument("-c",'--confdir', type=str, default="~/.motherless-dl", help='Program config path, default: ~/.motherless-dl/')
        self.args = parser.parse_args()
        
    def __call__(self):
        self.argparser()
        conf=Confdir(self.args.confdir)
        Database.load(conf)
        f=Favs(self.args.username)
        mediumlist=[Medium(x) for x in f]
        for m in mediumlist:
            m.download(self.args.destination,conf)
        Database.close()
        
class PageLoader(_Web):
    """
    Loads all of the pages from the favourites.
    """
    def __init__(self,username):
        self.user=username
        self.html=[]
        self.url="http://motherless.com/f/%s/all"%self.user # TODO: move to SiteSpecific

    def __call__(self):        
        self.html.append(self.get(self.url))
        self.getPages()

    def getPage(self,url):
        self.html.append(self.get(url))
        
    def getPages(self):
        #links=self.getLinks(self.html[0],href=self.filterForNextPageButton)
        links=self.getLinks(self.html[0],attrs={'href':re.compile(".*page=.*")}) # TODO: move to SiteSpecific
        for link in links:
            self.getPage(urljoin(self.url,link))
        
class Favs(_Web,set):
    """
    A list of all favourited urls.
    """
    def __init__(self,username):
        self.pageloader=PageLoader(username)
        self.pageloader()
        self.user=username
        self.favs=set([])
        for h in self.pageloader.html:
            self.getMediaLinks(h)
        self.favs=[urljoin(self.pageloader.url,x) for x in self.favs]
        self.update(self.favs)

    def getMediaLinks(self,html):
        self.favs.update(self.getLinks(html,attrs={"class":"img-container"})) # TODO: move to SiteSpecific
        


if __name__ == "__main__":
    Main()()

