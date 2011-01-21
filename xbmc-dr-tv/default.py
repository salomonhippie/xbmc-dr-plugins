import sys
import xbmc, xbmcgui, xbmcaddon, xbmcplugin
import re
from urllib2 import Request, urlopen, unquote

baseURL = "http://www.dr.dk/odp/"
allURL  = "default.aspx?template=flad_alle_programserier"
epsInfoUrl = "default.aspx?template=programserie&guid=" #concat with prog GUID
epsLinkUrl = "default.aspx?template=flad_programserie&guid=" #concat with prog GUID

def unescape(s):
        s = s.replace("&lt;", "<")
        s = s.replace("&gt;", ">")
        s = s.replace("&amp;", "&")
        return s

class DRtv:
	
	def __init__(self,h,p,a):
		self.handle = h
		self.pluginURL = p
		self.arg = a
		if self.arg.startswith("?show"):
			self.listEpisodes()
		else:
			self.listProgs()
	
	def getProgrammes(self, url):
		response = urlopen(Request(url))
		lines = response.readlines()
		reTitle = re.compile('.*<div class="programTitle">(.*)</div>')
		reLink = re.compile('.*<a href="(.*)">')
		reGUID = re.compile('.*<a href=".*guid=(.*)">')
		lookForLink = False
		title = "";
		link = "";
		pairs = []
		for line in lines:
			line = unescape(line)
			if lookForLink:
				# tmp = re.match(reUid, line)
				# if tmp:
				# 	guid = tmp.group(1)
				# 	print "DR GUID: " + guid
				# else:
				# 	print "DR NO GUID"
				# res = re.match(reLink, line)
				res = re.match(reGUID, line)
				if res:
					link = res.group(1)
					lookForLink = False
					pairs.append((title, link))
				# if res:
				# 	link = res.group(1)
				# 	lookForLink = False
				# 	pairs.append((title, link))
			else:
				res = re.match(reTitle, line)
				if res:
					title = res.group(1)
					lookForLink = True
		return pairs

	def getEpisodes(self, guid):
		response = urlopen(Request(baseURL + epsLinkUrl + guid))
		infoResponse = urlopen(Request(baseURL + epsInfoUrl + guid))
		lines = response.readlines()
		infoLines = infoResponse.readlines()
		reDate = re.compile('.*<div class="programTitle">.*<span class="date">(.*)</span></div>')
		reLink = re.compile('.*<a href="(.*)">')

		reInfoTitle = re.compile('.*>(.*)<.*')
		reInfoImg = re.compile('.*<img src="(.*)" .*')
		reInfoDesc = re.compile('.*>(.*)<.*')
		
		lookForLink = False
		title = ""
		link = ""
		desc = ""
		img = ""
		date = ""
		pairs = []
		for line in lines:
			line = unescape(line)
			if lookForLink:
				res = re.match(reLink, line)
				if res:
					link = res.group(1)
					lookForLink = False
			 		pairs.append((title, date, link, desc, img))
			else:
				res = re.match(reDate, line)
				if res:
					date = res.group(1)
					lookForLink = True
					## find info
					reInfoStart = re.compile('.*' + date + '.*')
					desc = ""
					img = ""
					title = ""
					for i in range(0, len(infoLines)):
						infoRes = re.match(reInfoStart, infoLines[i])
						if infoRes:
 							infoRes = re.match(reInfoDesc, infoLines[i+1])
							if infoRes:
								desc = infoRes.group(1)
								# print "DESC: " + desc
							infoRes = re.match(reInfoImg, infoLines[i-2])
							if infoRes:
								img = infoRes.group(1)
								# print "IMG: " + img
							infoRes = re.match(reInfoTitle, infoLines[i-1])
							if infoRes:
								title = infoRes.group(1)
								# print "TITLE: " + title
							break
		return pairs

	def getVideoURL(self, req):
		return req.get_full_url()
	
	def endDirs(self):
		xbmcplugin.endOfDirectory(self.handle)
	
	def epToItem(self, ep):
		li = xbmcgui.ListItem(ep[0] + " - " + ep[1])
		li.setInfo("video", {"title": ep[0], "plotoutline": ep[3]})
		li.setThumbnailImage(ep[4])
		return (self.getVideoURL(Request(ep[2])), li, False)

	def listEpisodes(self):
		showUrl = self.arg[6:]
		eps = self.getEpisodes(showUrl)
		eps.reverse()
		items = map(self.epToItem, eps);
		xbmcplugin.addDirectoryItems(self.handle, items, len(items))
		self.endDirs()
		
	def progToDir(self, prog):
		return (self.pluginURL+"?show=" + prog[1], xbmcgui.ListItem(prog[0]), True)

	def listProgs(self):
		progs = self.getProgrammes(baseURL+allURL)		
		dirs = map(self.progToDir, progs)
		xbmcplugin.addDirectoryItems(self.handle, dirs, len(dirs))
		self.endDirs()
			

if (__name__ == "__main__"):
	handle = int(sys.argv[1])
	pluginUrl = sys.argv[0]
	arg = sys.argv[2]
	
	tv = DRtv(handle, pluginUrl, arg)
	del tv

