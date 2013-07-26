#!/usr/bin/env python
# -*- coding: utf-8 -*- 
'''
Authr: João Juíz
'''
from motherless import *

class MainTest(Main):
    def __init__(self):
        pass
        
    def __call__(self):
        self.argparser()
        print self.args.destination
        
        
if __name__ == "__main__":
    MainTest()()

