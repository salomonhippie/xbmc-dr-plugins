
import sys
import xbmc, xbmcgui, xbmcaddon, xbmcplugin
import re
from urllib2 import Request, urlopen, unquote

baseURL = "http://www.dr.dk/odp/"
allURL  = "default.aspx?template=flad_alle_programserier"

def unescape(s):
        s = s.replace("&lt;", "<")
        s = s.replace("&gt;", ">")
        s = s.replace("&amp;", "&")
        return s


class DRTVPlugin:
	
	def __init__(self,h,p,a):
		self.handle = h
		self.pluginURL = p
		self.arg = a
	
	def getProgrammes(self, req):
		response = urlopen(req)
		lines = response.readlines()
		reTitle = re.compile('.*<div class="programTitle">(.*)</div>')
		reLink = re.compile('.*<a href="(.*)">')
		lookForLink = False
		title = "";
		link = "";
		pairs = []
		for line in lines:
			line = unescape(line)
			if lookForLink:
				res = re.match(reLink, line)
				if res:
					link = res.group(1)
					lookForLink = False
					pairs.append((title, link))
			else:
				res = re.match(reTitle, line)
				if res:
					title = res.group(1)
					lookForLink = True
		return pairs

	def getEpisodes(self, req):
		response = urlopen(req)
		lines = response.readlines()
		reTitle = re.compile('.*<div class="programTitle">.*<span class="date">(.*)</span></div>')
		reLink = re.compile('.*<a href="(.*)">')
		lookForLink = False
		title = "";
		link = "";
		pairs = []
		for line in lines:
			line = unescape(line)
			if lookForLink:
				res = re.match(reLink, line)
				if res:
					link = res.group(1)
					lookForLink = False
					pairs.append((title, link))
			else:
				res = re.match(reTitle, line)
				if res:
					title = res.group(1)
					lookForLink = True
		return pairs
	def getVideoURL(self, req):
		return req.get_full_url()


	
	def addDir(self,url,name,dir=True):
		xbmcplugin.addDirectoryItem(self.handle, self.pluginURL+url,xbmcgui.ListItem(name),dir)
	
	def addLink(self,url,name):
		item = xbmcgui.ListItem(name)		
		xbmcplugin.addDirectoryItem(self.handle,url,item)
	
	def endDirs(self):
		xbmcplugin.endOfDirectory(self.handle)
	
	def listShow(self):
		showUrl = self.arg[6:]
		self.eps = self.getEpisodes(Request(baseURL+showUrl))
		for ep in self.eps:
			self.addLink(self.getVideoURL(Request(ep[1])),ep[0])		

		self.endDirs()
		
	def listAll(self):
		self.progs = self.getProgrammes(Request(baseURL+allURL))		
		for prog in self.progs:
			self.addDir("?show="+prog[1],prog[0])
		self.endDirs()

	def playEpisode(self):
		epsUrl = self.arg[5:]
		vurl = self.getVideoURL(Request(epsUrl))
		
		self.endDirs()
	
	def doit(self):
		if (self.arg == '?all'):
			self.listAll()
		elif self.arg.startswith("?show"):
			self.listShow()
		elif self.arg.startswith("?eps"):
			self.playEpisode()
		else:
			self.addDir("?all","All")
			xbmcplugin.addDirectoryItem(self.handle, self.pluginURL, xbmcgui.ListItem(self.pluginURL), True)
			self.endDirs()
			



if (__name__ == "__main__"):
	handle = int(sys.argv[1])
	pluginUrl = sys.argv[0]
	arg = sys.argv[2]
	
	tv = DRTVPlugin(handle,pluginUrl,arg)
	tv.doit()
	del tv
	