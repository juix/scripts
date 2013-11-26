#!/usr/bin/env python
# -*- coding: utf-8 -*- 
'''
Authr: João Juíz

Literature:
    http://ceriksen.com/2012/07/26/firefox-sessionstore-js-and-privacy/. 26/10/2013
'''
from medium import Medium
import argparse,json,os,sys,urllib2,subprocess

class Main(object):
    def argparser(self):
        parser = argparse.ArgumentParser(description="Downloads motherless media from Iceweasel's/Firefox' open tabs. URLs of downloaded motherless.com items are printed to stdout.")
        parser.add_argument("-p", "--path", type=str, help='Path to ~/.mozilla/firefox/something/. First match of sessionstore.js if not specified.')
        parser.add_argument("-i", "--images-only", dest="images_only", action="store_true", default=False, help="Don't download videos")
        parser.add_argument("-o",'--destination', type=str, default=".", help='Save files here, defualt: ./')
        parser.add_argument("-s",'--sessionstore', action="store_true", default=False, help='Only remove downloaded tabs from sessionstore and quit')
        self.args = parser.parse_args()

    def __init__(self):
        pass
        
    def _log(self,text):
        #print text
        pass
        
    def firefoxIsOpen(self):
        return subprocess.call(["ps","-C","firefox","-C","iceweasel","-C","firefox-bin"],stdout=subprocess.PIPE) == 0
        
    def __call__(self):
        self.argparser()
        if not self.args.path:
            firefoxPath=self.getFirefoxPath()
            print >>sys.stderr, "Using sessionstore from %s."%firefoxPath
        else: firefoxPath=self.args.path
            
        if self.args.sessionstore and self.firefoxIsOpen() \
            and raw_input("Browser must be closed first. Continue anyway? [y/N]") != "y":
            exit(1)
        self._getLinks(firefoxPath,self.args.sessionstore)
        #print >> sys.stderr, len(self.urls)," Links"
        #for url in self.urls: self._download(url)
        
    def getFirefoxPath(self):
        for root, dirs, files in os.walk(os.path.expanduser("~/.mozilla/firefox/")):
            for file in files:
                if file=="sessionstore.js":
                    #return os.path.join(root, file)
                    return root
        
    def isValidUrl(self,url):
        return ("motherless.com" in url and "/search" not in url \
                        #and "/g/" not in url and "/gv/" not in url \
                        and "page=" not in url and "/term/" not in url \
                        and "/gi/" not in url and "/m/" not in url \
                        and "/f/" not in url and "/videos/" not in url)
    def _getLinks(self,firefoxPath,onlySessionstore=False):
        """
        @onlySessionstore Dont download anything, only remove existing media from sessionstore
        """
        sessionstore=os.path.join(firefoxPath,"sessionstore.js")
        with open( sessionstore ) as f:
            sstore=json.load(f)
        #urls=[ entry["url"] for entry in tab["entries"] for tab in window["tabs"] for window in sstore["windows"] ]
        #urls=[]
        for window in sstore["windows"]: 
            deleteItems=[]
            for tab in window["tabs"]: 
                    entry=tab["entries"][-1]
                    #if "scroll" not in entry: continue
                    url=entry["url"]
                    self._log(url)
                    if self.isValidUrl(url):
                        self._log("\tis valid motherless url")
                        m=Medium(url)
                        existsLocally=m.existsAtDestination(self.args.destination)
                        if onlySessionstore == False and not existsLocally:
                            self._download(m)
                        if onlySessionstore and existsLocally:
                            print "Remove from sessionstore:",url
                            deleteItems.append(tab)
            self._log("delete tabs")
            for tab in deleteItems:
                window["tabs"].remove(tab)
        #self.urls=urls
        if onlySessionstore:
            self._log("write sessionstore")
            with open(sessionstore, 'w') as outfile:
                json.dump(sstore, outfile)
        
    def _download(self,m):
        """
        @m      Instance of Medium = Medium("http://...")
        @return True if this url is a media item (leaf) that has/had been downloaded
        """
        #m=Medium(url)
        #if m.existsAtDestination(self.args.destination): return True
        try:
            self._log("\tload medium")
            m()
        except urllib2.HTTPError as e: 
            print m.websiteUrl
            print >> sys.stderr, e
            return False
        if m.isLeaf == False: return False
        
        if self.args.images_only == False or m.isPhoto:
            m.download(self.args.destination)
            #m.saveHtmlFile(self.args.destination)
            print m.websiteUrl
            return True
        return False

        
if __name__ == "__main__":
    Main()()

