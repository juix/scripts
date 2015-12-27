#!/usr/bin/env python
# -*- coding: utf-8 -*- 
'''
Authr: João Juíz
'''

#import re
#from urlparse import urljoin
import argparse
from medium import Medium
from database import Database
from confdir import Confdir

class Main(object):
    def __init__(self):
        pass
    
    def argparser(self):
        parser = argparse.ArgumentParser(description='Download an item from motherless.com')
        parser.add_argument("url", type=str, help='Address to fetch media from')
        parser.add_argument("-o",'--destination', type=str, default=".", help='Save files here')
        parser.add_argument("-f",'--force', action="store_true", help='Force downloading again')
        parser.add_argument("-c",'--confdir', type=str, default="~/.motherless-dl", help='Program config path, default: ~/.motherless-dl/')
        parser.set_defaults(force=False)
        self.args = parser.parse_args()
        
    def __call__(self):
        self.argparser()
        self.conf=Confdir(self.args.confdir)
        Database.load(conf)
        m=Medium(self.args.url)
        m.download(self.args.destination, conf, self.args.force)
        Database.close()

if __name__ == "__main__":
    Main()()

