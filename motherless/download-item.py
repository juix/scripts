#!/usr/bin/env python
# -*- coding: utf-8 -*- 
'''
Authr: João Juíz
'''

#import re
#from urlparse import urljoin
import argparse
from medium import Medium

class Main(object):
    def __init__(self):
        pass
    
    def argparser(self):
        parser = argparse.ArgumentParser(description='Download an item from motherless.com')
        parser.add_argument("url", type=str, help='Address to fetch media from')
        parser.add_argument("-o",'--destination', type=str, default=".", help='Save files here')
        self.args = parser.parse_args()
        
    def __call__(self):
        self.argparser()
        m=Medium(self.args.url)
        m()
        m.download(self.args.destination)

if __name__ == "__main__":
    Main()()

