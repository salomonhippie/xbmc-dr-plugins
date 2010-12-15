import os
import sys
import traceback
import xbmcgui
import xbmc

p1_listitem = xbmcgui.ListItem('P1')
p1_listitem.setInfo('music', {'Title': 'P1', 'Genre': 'Who knows?'})
p2_listitem = xbmcgui.ListItem('P2')
p2_listitem.setInfo('music', {'Title': 'P2', 'Genre': 'Who knows?'})
p3_listitem = xbmcgui.ListItem('P3')
p3_listitem.setInfo('music', {'Title': 'P3', 'Genre': 'Who knows?'})
p4_listitem = xbmcgui.ListItem('P4')
p4_listitem.setInfo('music', {'Title': 'P4', 'Genre': 'Who knows?'})

sky80s_listitem = xbmcgui.ListItem('Sky.fm')
sky80s_listitem.setInfo('music', {'Title': 'Sky.fm best of the 80s', 'Genre': '80s'})
skyoldies_listitem = xbmcgui.ListItem('Sky.fm')
skyoldies_listitem.setInfo('music', {'Title': 'Sky.fm oldies', 'Genre': 'Oldies'})

# pl = xbmc.PlayList(0) # create new music playlist
# pl.add(p3_url, p3_listitem)
# pl.add(p4_url, p4_listitem)

low    = "40000"
medium = "70000"
high   = "300000"

quality = [low, medium, high]
qstr = ["Low", "Medium", "High"]
urls = [('P1', "http://wmscr2.dr.dk/e02ch01m?wmcontentbitrate=", p1_listitem),
	('P2', "http://wmscr2.dr.dk/e02ch02m?wmcontentbitrate=", p2_listitem),
	('P3', "http://wmscr2.dr.dk/e02ch03m?wmcontentbitrate=", p3_listitem),
	('P4', "http://wmscr2.dr.dk/e04ch03m?wmcontentbitrate=", p4_listitem),
	# ('Sky.fm 80s', "mms://88.191.102.29:80/the80s", sky80s_listitem),
	# ('Sky.fm oldies', "mms://88.191.102.239:80/oldies", skyoldies_listitem),
]

class RadioGUI(xbmcgui.Window):	
	def __init__(self):
		self.quality = 0
		self.index = 0
		self.playing = False
	 	self.title = xbmcgui.ControlLabel(100,100,200,40,'')
		self.qlbl  = xbmcgui.ControlLabel(100,120,200,60,'')
		self.addControl(self.title)
		self.addControl(self.qlbl)
		self.player = xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER);
		self.__updateGUI()
				
	def __del__(self):
		#self.player.stop()
		pass
	
	def __playCurrent(self):
		qstr = quality[self.quality]
		self.player.play(urls[self.index][1]+qstr, urls[self.index][2])
		self.playing = True
		self.__updateGUI()

	def __stop(self):
		self.player.stop()
		self.playing = False
		self.__updateGUI()

	def __qualityInc(self):
		self.quality += 1
		if (self.quality >= len(quality)):
			self.quality = 0
		self.__updateGUI()

	def __qualityDec(self):
		self.quality -= 1
		if (self.quality < 0):
			self.quality = max(len(quality) - 1, 0)
		self.__updateGUI()

	def __next(self):
		self.index += 1
		if (self.index >= len(urls)):
			self.index = 0
		self.__updateGUI()

	def __prev(self):
		self.index -= 1
		if (self.index < 0):
			self.index = max(len(urls) - 1, 0)
		self.__updateGUI()


	def __updateGUI(self):
		txt = urls[self.index][0]
		if (self.playing):
			txt += ' - playing'
		self.title.setLabel(txt)
		self.qlbl.setLabel("Quality: " + qstr[self.quality])
		pass

	def onAction(self, action):
 		"""Handle user input events."""
 		try: 
 			if action.getId() == 10: # exit
				# if (self.playing):
				#  	self.__stop()
				# else:
				self.close()

			if action.getId() == 1: # left
				self.__prev()

			if action.getId() == 2: # right
				self.__next()
								
			if action.getId() == 3: # up
				self.__qualityInc()

			if action.getId() == 4: # down
				self.__qualityDec()

			if action.getId() == 7: # "enter"
					self.__playCurrent()

 		except:
 			xbmc.log('Exception (onAction): ' + str(sys.exc_info()[0]))
 			traceback.print_exc()
 			self.close()
			 
w = RadioGUI()
w.doModal()
del w
