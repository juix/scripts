#!/usr/bin/env python
# -*- coding: utf-8 -*- 
'''
Authr: João Juíz
'''

import sys,os,re,parsedatetime
import lxml.etree
from lxml.cssselect import CSSSelector
from myDb import ExtendedDB
import config


htmldir = os.path.expanduser("~/.motherless-dl/html")

class HTMLMixin(object):

    def __call__(self):
        #self.handleHtml("C5B1863")
        #self.handleAllHtml()
        pass

    def writeAllHtml(self):
        """ read all files from ~/.motherless-dl/html/$ID and write features to DB
        if $ID does not already exist. """
        print("Html to database")
        ids = self.getAllRetrievedIds()
        ids_todo = ids.difference(self.getAllDbIds())
        for i in ids_todo:
            sys.stderr.write("\t%s\n"%i)
            self.handleHtml(i)
        self.db.commit()

    def handleHtml(self, id_):
        """ handle a single html file and write to DB """
        with open(os.path.join(htmldir,id_)) as f:
            #self.xmlTree = fromstring(f.read())
            self.xmlTree = lxml.etree.HTML(f.read())
        
        uploaderName, uploaderLink = self.extractA("div.thumb-member-username a")
        uploader = (uploaderName, uploaderLink)
        title = self.find("#view-upload-title")[0].text.strip()
        views = self.extractHInfo("Views").replace(",","")
        favourited = self.extractHInfo("Favorited").replace(",","")
        time = self.parseDate(self.extractHInfo("Uploaded"))
        tags = [(e.text,e.get("href")) for e in self.find("#media-tags-container a")]
        groups = [(e.text,e.get("href")) for e in self.find("#media-groups-container a")]
        comments = [self.parseComment(c) for c in self.find(".media-comment-contents")]
        
        self.db.query("DELETE FROM users WHERE link=%s",(uploaderLink,))
        self.db.save("users",link=uploaderLink,name=uploaderName)
        
        self.db.query("DELETE FROM medium WHERE id=%s",(id_,))
        self.db.save("medium",id=id_,uploaderlink=uploaderLink,
            title=title,views=views,favourited=favourited,
            time=time)
        
        for tag in tags:
            self.db.save("tags",id=id_,name=tag[0],link=tag[1])
        for group in groups:
            self.db.save("groups",id=id_,name=group[0],link=group[1])
        for c in comments:
            author,authorlink = c["author"]
            self.db.query("DELETE FROM users WHERE link=%s",(authorlink,))
            self.db.save("users",link=authorlink,name=author)
            self.db.save("comments",id=id_,authorlink=authorlink,time=c["time"],content=c["content"])

        # parse H file
        hfile = os.path.join(htmldir,"H%s"%id_)
        if not os.path.exists(hfile): 
            sys.stderr.write("WARNING H%s does not exist.\n"%id_)
            return
        with open(hfile) as f:
            self.xmlTree = lxml.etree.HTML(f.read())
        recommended = set([e.get("data-codename") for e in self.find("div[data-codename]")])
        for r in recommended:
            self.db.save("also_favourited",id=id_,id_also=r)
        
        del self.xmlTree

    def parseDate(self, s):
        c = parsedatetime.Constants()
        c.YearParseStyle = 0
        c.DOWParseStyle = -1 # oder 0
        c.CurrentDOWParseStyle = False
        dt,flags = parsedatetime.Calendar(c).parseDT(s)
        if flags == 0:
            raise Exception("WARNING: Cannot parse date '%s'."%s)
        return dt
        
    def parseComment(self, c):
            """ each comment calls this function """
            a = c.xpath("h4/a")[0]
            author = a.text.strip()
            authorHref = a.get("href")
            time = c.xpath("*[@class='media-comment-meta']")[0].text.strip()
            content = c.xpath("div[@style]")[-1].xpath("string()").strip()
            return dict(author=(author,authorHref),time=self.parseDate(time),content=content)
        
    def extractA(self, selector):
        """ return text and link of an a-tag """
        l = self.find(selector)
        if len(l) == 0: raise Exception("ElementNotFound: %s"%selector)
        e = l[0]
        if "href" not in e.keys(): raise Exception("AttributeNotFound: 'href' in %s."%selector)
        href = e.get("href")
        text = e.text.strip()
        return text,href
        
    def extractHInfo(self, text):
        """ return text of parent element. e.g.
        "<h1>News</h1> This is good news!" -> extractHInfo("News") = "News This is good news!"
        """
        return self.findHeadline(text).xpath("text()")[-1].strip()
        
    def findHeadline(self, text):
        h = self.findByText(text)
        if h is None: return None
        else: return h.xpath("..")[0]
        
    def findByText(self, text):
        e = self.xmlTree.xpath("//*[contains(text(),'%s')]"%text)
        if len(e) == 0: return None
        else: return e[0]
    
    def find(self, selector):
        """ find by css """
        sel = CSSSelector(selector)
        return sel(self.xmlTree)
        

class IdsMixin(object):
    """ Functions concerning file search """

    def getAllDbIds(self):
        """ get all ids stored in DB """
        self.db.query("SELECT id FROM medium")
        return [r[0] for r in self.db.cursor.fetchall()]

    def writeIdsToDb(self):
        print("Updating likes/dislikes in DB")
        db = self.db
        self.refreshStoredFiles()

        all_ = self.getAllRetrievedIds()
        #for x in all_: db.query("INSERT INTO ids_all VALUES (%s)",(x,))
        #db.commit()
        storedFiles = self.getStoredFiles()
        storedIds = [i for i,f in storedFiles]
        self.db.query("DELETE FROM ids_dislikes")
        self.db.query("DELETE FROM ids_likes")
        
        dislikes = all_.difference(storedIds)
        for x in dislikes: db.query("INSERT INTO ids_dislikes VALUES (%s)",(x,))
        likes = set([i for i,f in storedFiles if self.isFav(f)])
        for x in likes: db.query("INSERT INTO ids_likes VALUES (%s)",(x,))
        #testset = set(storedIds).difference(likes)
        print("\t%d files stored."%len(set(storedIds)))
        self.db.commit()
        
    def getAllRetrievedIds(self):
        """ get all ids ever downloaded """
        return set([x for x in os.listdir(htmldir)
            if not x.startswith("H")])

    def isFav(self, path):
        root = os.path.dirname(path)
        return "favs" in root or "keep" in root
    
    def pathToId(self, f):
            r = re.findall(".*OTHERLESS\.COM\ \-\ ([^\.\-\ ]*)",f)
            if len(r) == 0: return None # not a ml-file
            if len(r[0]) > 7:
                sys.stderr.write("%s, %s\n"%(r[0],f))
            return r[0]
    
    def walkAll(self):
        """ return all file paths from motherless' config.downloadDirs """
        for d in config.downloadDirs:
            for f in self.walkDir(d):
                yield f
    
    def walkDir(self, path):
        """ return all potentially useful file paths from @path """
        for root, dirs, files in os.walk(path):
            if "by-id" in root or os.path.basename(root) == "by-rating": continue
            for f in files: 
                if f.startswith("_"): continue
                yield os.path.join(root,f)
                
    def _getPredictedLikes(self):
        self.db.query("SELECT id FROM predictions WHERE cls = 1")
        likes = [r[0] for r in self.db.cursor.fetchall()]
        return likes
        
    def linkPredictedLikes(self):
        """ link all as like predicted files to config.predictedLikesDir """
        self._forallPredictedLikes(os.symlink)
    
    def _forallPredictedLikes(self, func):
        """ call func(src, dest) for each file predicted as "like" """
        destDir = config.predictedLikesDir
        if not os.path.lexists(destDir): os.makedirs(destDir)
        likes = self._getPredictedLikes()
        stored = dict(self.getStoredFiles())
        log = []
        for i in likes:
            f = stored[i]
            dest = os.path.join(destDir,os.path.basename(f))
            if os.path.lexists(dest): 
                sys.stderr.write("WARNING: %s exists more than once.\n"%i)
                continue
            func(f,dest)
            #print(f,dest)
            log.append((f,dest))
        import json
        with open("/tmp/motherless-ai.log","w") as f:
            json.dump(log,f)
            
    def mvPredictedLikes(self):
        """ link all as like predicted files to config.predictedLikesDir """
        self._forallPredictedLikes(os.rename)
        
    def getStoredFiles(self):
        """ get list of (id,path) of all files stored on hd according to DB """
        self.db.query("SELECT id, path FROM file_system")
        return [(r[0],r[1]) for r in self.db.cursor.fetchall()]
        
    def refreshStoredFiles(self):
        """ write all file paths in config.downloadDirs and their ids to DB """
        self.db.query("DELETE FROM file_system")
        for f in self.walkAll():
            i = self.pathToId(f)
            if i is None: continue
            self.db.query("INSERT INTO file_system VALUES (%s,%s,%s)",(i,f,self.isFav(f)))
        self.db.commit()
        
    def _del_eraseFiles(self):
        """ erase files removed in config.predictedLikesDir """
        linked = self._getPredictedLikes()
        existing = set([self.pathToId(f) for f in self.walkDir(config.predictedLikesDir)]).difference([None])
        removed = set(linked).difference(existing)
        self.db.query("SELECT path FROM file_system WHERE id IN %s",(tuple(removed),))
        removedPaths = [r[0] for r in self.db.cursor.fetchall()]
        sys.stderr.write("Links to these files have been removed:\n\n")
        for f in removedPaths: print(f)
        for i in removed:
            for by_id_path in config.byIdPaths:
                path = os.path.join(by_id_path,i)
                if os.path.exists(path): print(path)
        
    def checkEmptyLikesDir(self):
        pld = config.predictedLikesDir
        if os.path.exists(pld) and len(os.listdir(pld)) > 0:
            raise Exception("ERROR: %s is not empty!"%pld)
        return True
        
class Main(IdsMixin,HTMLMixin):

    def __init__(self):
        self.db = ExtendedDB(commitOnClose=False)

DbPen = Main
        
    
if __name__ == "__main__":
    Main()()

