#!/usr/bin/env python
# -*- coding: utf-8 -*- 
'''
Authr: João Juíz
'''

import argparse,os,sys

class Main(object):
    def __init__(self):
        pass
    
    def argparser(self):
        parser = argparse.ArgumentParser(description='Searches for unreferenced files in by-id/ and prints them to stdout')
        parser.add_argument("-o",'--destination', type=str, default=".", help='Search here')
        self.args = parser.parse_args()
        
    def __call__(self):
        self.argparser()
        referenced=self._loadReferenced()
        existing=set(os.listdir(os.path.join(self.args.destination,"by-id")))
        trash=existing.difference(referenced)
        size=0
        for x in trash: size+=os.path.getsize(os.path.join(self.args.destination,"by-id",x))
        print >> sys.stderr, size/1024/1024, "MB"
        print >> sys.stderr, len(trash), "files"
        print "\n".join(trash)
        
        #testing:
        #print "88750E7" in trash
        #print "1B4A9C7" in trash
        #print "E39A8FE" in trash
        
    def _loadReferenced(self):
	    TODO: alle links laden, nicht nur in der Verzeichnistiefe 1
        r=set()
        for element in os.listdir(self.args.destination):
            if not element.startswith("by-name"): continue
            r.update(self._findLinks(os.path.join(self.args.destination,element)))
        return r
            
    def _findLinks(self,path):
        r=set()
        for element in os.listdir(path):
            l=self._resolveLink(os.path.join(path,element))
            if l != None: r.add(l)
        return r
        
    def _resolveLink(self,path):
        try:
            return os.path.basename(os.readlink(path))
        except OSError: return None

if __name__ == "__main__":
    Main()()

