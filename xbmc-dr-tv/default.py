import os
import sys
import traceback
import xbmcgui
import xbmc
import re
from urllib2 import Request, urlopen, unquote

baseURL = "http://www.dr.dk/odp/"
allURL  = "default.aspx?template=flad_alle_programserier"


def unescape(s):
        s = s.replace("&lt;", "<")
        s = s.replace("&gt;", ">")
        s = s.replace("&amp;", "&")
        return s


class TVGUI(xbmcgui.Window):	
	def __init__(self):
		self.indexProgs = 0
		self.indexEpis = 0
		self.doEpis = False
	 	self.progTitle = xbmcgui.ControlLabel(100,100,500,60,'')
		self.episTitle  = xbmcgui.ControlLabel(100,120,200,60,'')
		self.addControl(self.progTitle)
		self.addControl(self.episTitle)
		self.player = xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER);
		self.progs = self.getProgrammes(Request(baseURL+allURL))
		self.epis = []
		self.__updateGUI()

	def __del__(self):
		#self.player.stop()
		pass

	def __playCurrent(self):
		if self.doEpis:
			self.player.play(self.getVideoURL(Request(self.epis[self.indexEpis][1])))
			#self.__updateGUI()
			pass
		else:
			self.indexEpis = 0
			self.epis = self.getEpisodes(Request(baseURL+self.progs[self.indexProgs][1]))
			self.doEpis = True
			self.__updateGUI()
			
	def __next(self):
		if self.doEpis:
			self.indexEpis += 1
			if (self.indexEpis >= len(self.epis)):
				self.indexEpis = 0
		else:
			self.indexProgs += 1
			if (self.indexProgs >= len(self.progs)):
				self.indexProgs = 0
		self.__updateGUI()

	def __prev(self):
		if self.doEpis:
			self.indexEpis -= 1
			if (self.indexEpis < 0):
				self.indexEpis = max(len(self.epis) - 1, 0)
		else:
			self.indexProgs -= 1
			if (self.indexProgs < 0):
				self.indexProgs = max(len(self.progs) - 1, 0)
		self.__updateGUI()

	def __updateGUI(self):
		# if (self.playing):
		# 	txt += ' - playing'
		self.progTitle.setLabel(self.progs[self.indexProgs][0])
		if self.doEpis:
			if len(self.epis) == 0:
				self.episTitle.setLabel("Empty List")
			else:
				self.episTitle.setLabel(self.epis[self.indexEpis][0])
		else:
			self.episTitle.setLabel("")

	def getVideoURL(self, req):
		return req.get_full_url()
		# response = urlopen(req)
		# lines = response.readlines()
		# pass

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
					
	def onAction(self, action):
 		"""Handle user input events."""
 		try: 
 			if action.getId() == 10: # exit
				if self.doEpis:
					self.doEpis = False
					self.__updateGUI()
				else:
					self.close()

			if action.getId() == 1: # left
				self.__prev()

			if action.getId() == 2: # right
				self.__next()
								
			if action.getId() == 3: # up
				if self.doEpis:
					self.doEpis = False
					self.__updateGUI()

			if action.getId() == 4: # down
				if not self.doEpis:
					self.__playCurrent()

			if action.getId() == 7: # "enter"
					self.__playCurrent()

 		except:
 			xbmc.log('Exception (onAction): ' + str(sys.exc_info()[0]))
 			traceback.print_exc()
 			self.close()
			 
w = TVGUI()
w.doModal()
del w
