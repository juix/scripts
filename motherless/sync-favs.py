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

class Main(object):
    def __init__(self):
        pass
    
    def argparser(self):
        parser = argparse.ArgumentParser(description='Sync motherless.com favourites to local directory')
        parser.add_argument("-u",'--username', type=str, required=True, help='Sync favourites of this user')
        parser.add_argument("-o",'--destination', type=str, required=True, help='Save files here')
        parser.add_argument("-l",'--recreate-links', dest="links", action="store_true", required=False, help='Create symlinks of already downloaded files')
        parser.set_defaults(links=False)
        self.args = parser.parse_args()
        
    def __call__(self):
        self.argparser()
        f=Favs(self.args.username)
        mediumlist=[Medium(x) for x in f]
        for m in mediumlist:
            if (not m.existsAtDestination(self.args.destination)):
                m()
                m.download(self.args.destination)
            elif self.args.links:
                FW.error("Recreate Symlink")
                m()
                m.createSymlink(self.args.destination)
            #else:
            #    m()
            #    m.saveHtmlFile(self.args.destination)
        self._printDiffs(mediumlist)
        
    def _printDiffs(self,mediumlist):
        localDir=os.path.join(self.args.destination,"by-id")
        server=set([x.id for x in mediumlist])
        local=set([f for f in os.listdir(localDir) if os.path.isfile(os.path.join(localDir,f)) ])
        diff=local.difference(server)
        if len(diff) == 0: return
        FW.error("")
        FW.error("###################################################")
        FW.error("Filenames which exist on your computer but not in your motherless favourites are printed to stdout.")
        for x in diff: print x
        
class PageLoader(_Web):
    """
    Loads all of the pages from the favourites.
    """
    def __init__(self,username):
        self.user=username
        self.html=[]
        self.url="http://motherless.com/f/%s/all"%self.user

    def __call__(self):        
        self.html.append(self.get(self.url))
        self.getPages()

    def getPage(self,url):
        self.html.append(self.get(url))
        
    def getPages(self):
        #links=self.getLinks(self.html[0],href=self.filterForNextPageButton)
        links=self.getLinks(self.html[0],attrs={'href':re.compile(".*page=.*")})
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
        self.favs.update(self.getLinks(html,attrs={"class":"img-container"}))
        


if __name__ == "__main__":
    Main()()

