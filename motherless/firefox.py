#!/usr/bin/env python
# -*- coding: utf-8 -*- 
'''
Authr: João Juíz

Literature:
    http://ceriksen.com/2012/07/26/firefox-sessionstore-js-and-privacy/. 26/10/2013
'''
import argparse,json,os,sys,urllib2,subprocess
from medium import Medium, NoLeafException
from database import Database
from confdir import Confdir

class Loggable(object):
    def _log(self,text):
        #print text
        pass
        

class Main(Loggable):
    def argparser(self):
        parser = argparse.ArgumentParser(description="Downloads motherless media from Iceweasel's/Firefox' open tabs. URLs of downloaded motherless.com items are printed to stdout. Skips duplicates.")
        parser.add_argument("-p", "--path", type=str, help='Path to ~/.mozilla/firefox/something/sessionstore.js. First match of sessionstore.js if not specified.')
        parser.add_argument("-i", "--images-only", dest="images_only", action="store_true", default=False, help="Don't download videos")
        parser.add_argument("-o",'--destination', type=str, default=".", help='Save files here, defualt: ./')
        parser.add_argument("-c",'--confdir', type=str, default="~/.motherless-dl", help='Program config path, default: ~/.motherless-dl/')
        parser.add_argument("-s",'--sessionstore', action="store_true", default=False, help='Only remove downloaded tabs from sessionstore and quit')
        self.args = parser.parse_args()

    def __init__(self):
        pass
        
    def firefoxIsOpen(self):
        return subprocess.call(["ps","-C","firefox","-C","iceweasel","-C","firefox-bin"],stdout=subprocess.PIPE) == 0
        
    def __call__(self):
        self.argparser()
        self.conf=Confdir(self.args.confdir)
        if not self.args.path:
            firefoxPath=self.getFirefoxPath()
            print >>sys.stderr, "Using sessionstore from %s."%firefoxPath
        else: firefoxPath=self.args.path
            
        if self.args.sessionstore and self.firefoxIsOpen() \
            and raw_input("Browser must be closed first. Continue anyway? [y/N]") != "y":
            exit(1)
        Database.load(self.conf)
        sstore=Sessionstore(firefoxPath)
        if self.args.sessionstore:
            sstore.filterStorage(lambda url:self.isValidUrl(url) and Medium(url).downloadFinished())
            sstore.save()
        else:
            urls=sstore.getUrls()
            for i, url in enumerate(set(urls)):
                    if self.isValidUrl(url):
                        self._log("\tis valid motherless url")
                        sys.stdout.write("\r  ================>> %2.0f %%" % (100.0/len(urls)*i))
                        sys.stdout.flush()
                        m=Medium(url)
                        if (not m.isBeingDownloaded()) and (not Database.hasUrl(url)):
                            self._downloadThread(m)
            sys.stdout.write("\n")
        Database.close()
        #print >> sys.stderr, len(self.urls)," Links"
        #for url in self.urls: self._download(url)
        
    def getFirefoxPath(self):
        for root, dirs, files in os.walk(os.path.expanduser("~/.mozilla/firefox/")):
            for file in files:
                if file=="sessionstore.js":
                    return os.path.join(root, file)
                    #return root
        
    def isValidUrl(self,url):
        return ("motherless.com" in url and "/search" not in url \
                        #and "/g/" not in url and "/gv/" not in url \
                        and "page=" not in url and "/term/" not in url \
                        and "/gi/" not in url and "/m/" not in url \
                        and "/f/" not in url and "/videos/" not in url)

        
    def _downloadThread(self,m):
        self._download(m)
        Database.putUrl(m.websiteUrl)
        
    def _download(self,m):
        """
        @m      Instance of Medium = Medium("http://...")
        @return True if this url is a media item (leaf) that has/had been downloaded
        """
        #m=Medium(url)
        if (m.downloadFinished() or m.isBeingDownloaded()): return True
        
        try:
            self._log("\tload medium")
            m._retrieveProperties()
        except urllib2.HTTPError as e: 
            print m.websiteUrl
            print >> sys.stderr, e
            return False
        if m.isLeaf == False: return False
        
        if self.args.images_only == False or m.isPhoto:
            try:
                m.download(self.args.destination,self.conf)
            except NoLeafException: return False
            #m.saveHtmlFile(self.args.destination)
            print m.websiteUrl
            return True
        return False

class Sessionstore(Loggable):
    def __init__(self,firefoxPath):
        self.firefoxPath=firefoxPath
        
        # backwards compability in case "firefoxPath" is
        # still given as a path to the firefox directory and not to the sessionstore.js
        if os.path.isdir(firefoxPath): 
            self.sstorePath=os.path.join(firefoxPath,"sessionstore.js")
        else:
            self.sstorePath=firefoxPath
        
    def getUrls(self):
        self._load()
        self.getUrls = lambda:self.urls
        return self.urls
        
    def filterStorage(self,filterfunction):
        self._load(filterfunction)
    
    def _load(self,filterfunction=lambda url:False):
        """
        @filterfunction(url) Url is removed if return value is True
        @return [urls]
        """
        with open( self.sstorePath ) as f:
            sstore=json.load(f)
        #urls=[ entry["url"] for entry in tab["entries"] for tab in window["tabs"] for window in sstore["windows"] ]
        urls=[]
        for window in sstore["windows"]: 
            deleteItems=[]
            for tab in window["tabs"]: 
                    entry=tab["entries"][-1]
                    #if "scroll" not in entry: continue
                    url=entry["url"]
                    self._log(url)
                    if filterfunction(url):
                            print "Remove from sessionstore:",url
                            deleteItems.append(tab)
                    else: urls.append(url)
            self._log("delete tabs")
            for tab in deleteItems:
                window["tabs"].remove(tab)
        self.urls=urls
        self.content=sstore

    def save(self):
            self._log("write sessionstore")
            with open(self.sstorePath, 'w') as outfile:
                json.dump(self.content, outfile)
        
if __name__ == "__main__":
    Main()()

