#!/usr/bin/env python
# -*- coding: utf-8 -*- 
'''
Authr: João Juíz
'''
from medium import Medium
import argparse,json,os,sys,urllib2

class Main(object):
    def argparser(self):
        parser = argparse.ArgumentParser(description="Downloads motherless media from Iceweasel's/Firefox' open tabs. URLs of downloaded motherless.com items are printed to stdout.")
        parser.add_argument("path", type=str, help='Path to ~/.mozilla/firefox/something/')
        parser.add_argument("-i", "--images-only", dest="images_only", action="store_true", default=False, help="Don't download videos")
        parser.add_argument("-o",'--destination', type=str, default=".", help='Save files here')
        self.args = parser.parse_args()

    def __init__(self):
        pass
        
    def __call__(self):
        self.argparser()
        self._getLinks()
        print >> sys.stderr, len(self.urls)," Links"
        for url in self.urls: self._download(url)
        
    def _getLinks(self):
        with open( os.path.join(self.args.path,"sessionstore.js") ) as f:
            sstore=json.load(f)
        #urls=[ entry["url"] for entry in tab["entries"] for tab in window["tabs"] for window in sstore["windows"] ]
        urls=[]
        for window in sstore["windows"]: 
            for tab in window["tabs"]: 
                for entry in tab["entries"]: 
                    if "motherless.com" in entry["url"]:
                        urls.append(entry["url"])
        self.urls=urls
        
    def _download(self,url):
        m=Medium(url)
        if m.existsAtDestination(self.args.destination): return
        try:
            m()
        except urllib2.HTTPError as e: 
            print url
            print >> sys.stderr, e
            return
        if m.isLeaf == False: return
        
        if self.args.images_only == False or m.isPhoto:
            if not m.existsAtDestination(self.args.destination): m.download(self.args.destination)
            else: m.saveHtmlFile(self.args.destination)
            print url

        
if __name__ == "__main__":
    Main()()

