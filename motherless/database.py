#!/usr/bin/env python
# -*- coding: utf-8 -*- 
'''
Authr: João Juíz
Database for the motherless downloader. It stores the IDs of downloaded files, fetched urls, etc.
'''
import sqlite3,os
from framework import Processes

class Database(object):
    """
    static class
    """
    
    @classmethod
    def load(self,path):
        if "path" in self.__dict__ and path==self.path: return
        self.path=path
        filename=os.path.join(path,".ml.db")
        creating=not os.path.exists(filename)
        self.conn=sqlite3.connect(filename)
        self.c=self.conn.cursor()
        self.pid=os.getpid()
        if creating: self._create()
        
    @classmethod
    def close(self):
        self.conn.commit()
        self.conn.close()

    @classmethod
    def _create(self):
        self.c.execute('CREATE TABLE urls (url string)')
        self.c.execute('CREATE TABLE ids (id string)')
        self.c.execute('CREATE TABLE activeDownloads (id string, pid int)')
        self._update()
        
    @classmethod
    def _update(self):
        idPath=os.path.join(self.path,"by-id")
        if os.path.exists(idPath):
            ids=os.listdir(idPath)
            self.c.executemany('INSERT INTO ids VALUES (?)',[(x,) for x in ids])
            self.conn.commit()
        
    @classmethod
    def hasId(self,s):
        return self.c.execute("SELECT id FROM ids WHERE id=?",(s,)).fetchone()!=None
    
    @classmethod
    def hasUrl(self,s):
        return self.c.execute("SELECT url FROM urls WHERE url=?",(s,)).fetchone()!=None
    
    @classmethod
    def _putId(self,s):
        self.c.execute("INSERT INTO ids VALUES (?)",(s,))
        self.conn.commit()
    
    @classmethod
    def putUrl(self,s):
        self.c.execute("INSERT INTO urls VALUES (?)",(s,))
        self.conn.commit()

    @classmethod
    def notify_startDownload(self,s):
        self.c.execute("INSERT INTO activeDownloads VALUES (?,?)",(s,self.pid))
        self.conn.commit()

    @classmethod
    def isDownloading(self,s):  # FIXME: prohibit two processes from entering the critical section at the same time! e.g. using lockfile
        return False
        pidQuest=self.c.execute("SELECT pid FROM activeDownloads WHERE id=?",(s,)).fetchone()
        if pidQuest == None: return False
        pid=pidQuest[0]
        if not Processes.isRunning(pid):
            self.c.execute("DELETE FROM activeDownloads WHERE id=?",(s,))
            return False
        else:
            return True
        
    @classmethod
    def notify_finishedDownload(self,s):
        self.c.execute("DELETE FROM activeDownloads WHERE id=?",(s,))
        self._putId(s)
        
