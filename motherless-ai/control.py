#!/usr/bin/env python
# -*- coding: utf-8 -*- 
'''
Authr: João Juíz
'''

import sys,os, argparse

class Main(object):

    def argparser(self):
        parser = argparse.ArgumentParser(description='What this program does')
        #parser.add_argument("param", type=str, help='Parameter Description')
        parser.add_argument("-d",'--database', default=False, action='store_true', help='Update database')
        parser.add_argument("-m",'--matrix', default=False, action='store_true', help='Update feature matrix')
        parser.add_argument("-c",'--classify', default=False, action='store_true', help='Classify')
        parser.add_argument("-x",'--chi2', default=False, action='store_true', help='Print chi² test. deprecated.')
        parser.add_argument("-r",'--report', default=False, action='store_true', help='Crossvalidation report')
        #parser.add_argument("-v",'--verbose', default=False, action='store_true', help='Fehlerausgabe')
        #parser.add_argument("-o",'--destination', type=str, default=".", help='Example Parameter')
        self.args = parser.parse_args()

    def __init__(self):
        pass
        
    def __call__(self):
        self.argparser()
        from makeMatrix import MatrixFactory
        from classify import Classifier
        if self.args.database:
            from makeDB import DbPen
            DbPen().writeAllHtml()
            DbPen().writeIdsToDb()
        if self.args.matrix:
            MatrixFactory().writeToFile()
        if self.args.chi2:
            Classifier().chi2()
        if self.args.report:
            Classifier().crossvali()
        if self.args.classify:
            Classifier().classify()

if __name__ == "__main__":
    Main()()        
