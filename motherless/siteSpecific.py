#!/usr/bin/env python
# -*- coding: utf-8 -*- 
'''
Authr: João Juíz
'''
import re
from urlparse import urlparse


class WebsiteChangedError(Exception): pass

class MotherlessSpecific(object):
    @staticmethod
    def getNumFaved(html):
        return int(re.findall("Favorited\D*(\d*)",html, re.S)[0]) #+re.I

    @classmethod
    def getVideoUrl(self,soup):
        div=self._getDiv(soup)
        r=re.findall("(http\:([^ \n\r\t\"']*)\.(mp4|flv))",div.getText())
        if len(r)==0:
            raise WebsiteChangedError("No video found.")
        return r[0][0]
    
    @staticmethod
    def getName(soup):
        return soup.title(text=True)[0]

    @classmethod
    def isPhoto(self,soup): 
        return len(self._getDiv(soup).findAll("img"))>0

    @staticmethod
    def _getDiv(soup):
        div=soup.findAll(id='media-media')
        div2=soup.findAll(id='full_image')
        if len(div)>0: return div[0]
        elif len(div2)>0: return div2[0]
        else:
            raise WebsiteChangedError("No media found. Probably website code changed.")
            
    @staticmethod
    def _getA(soup):
        a=self._getDiv(soup).findAll("a")
        if len(a)>0: return a[0]
        else:
            raise WebsiteChangedError("No A-Tag found in div. Probably website code changed.")
            
    #@staticmethod
    #def getLargepicUrl(soup):
    #    href=self._getA(soup).href
    #    if "?full" in href: return href
    #    else return None
    
    @staticmethod
    def isLeaf(soup):
        """
        @return True, if this is an item. Otherwise this is a gallery
        """
        div=soup.findAll(id='media-media')
        div2=soup.findAll(id='full_image')
        return (len(div)+len(div2)>0)

    @staticmethod
    def getPicUrl(soup):
        links=soup.findAll("link",rel="image_src")
        if len(links)==0: raise WebsiteChangedError("no img found.")
        href = links[0].get("href")
        return href
        #fullimg = soup.findAll(id='thepic')
        #if len(fullimg)>0:
        #    return fullimg[0].src
        #else:
        #    imgs=self._getA(soup).findAll("img")
        #    if len(imgs)==0:
        #        raise WebsiteChangedError("No img in A-Tag found.")
        #    return imgs[0].src

