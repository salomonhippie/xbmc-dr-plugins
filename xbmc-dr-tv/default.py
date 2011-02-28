import sys
import xbmc, xbmcgui, xbmcaddon, xbmcplugin
import re
import simplejson as json
from urllib2 import Request, urlopen, unquote

baseURL = "http://www.dr.dk/NU/api/"
allURL  = "programseries"

imgWidth = '415'
imgHeight = '233'

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
		j = json.loads(response.read())
		res = []
		for obj in j:
			res.append(obj)
		return res

	def getEpisodes(self, guid):
		url = baseURL + allURL + '/' + guid + '/videos'
		response = urlopen(Request(url))

		return json.loads(response.read())

	def getVideoURL(self, req):
		response = urlopen(req)
		j = json.loads(response.read())
		# print j
		return ((j['links'])[0])['uri']
	
	def endDirs(self, cache=False):
		xbmcplugin.endOfDirectory(self.handle, True, cache, False)
	
	def epToItem(self, ep):
		# print ep
		vurl = self.getVideoURL(Request(ep['videoResourceUrl']))

		playpath = '';
		url = '';
		if vurl.startswith('mms:'):
			url = vurl
		else:
			parts = vurl.split('mp4:')
			url = parts[0]
			playpath = 'mp4:' + parts[1]
			

		# print 'PUB: ' + ep['publishTime']
			
		li = xbmcgui.ListItem(label = ep['title'] + ' - ' + ep['formattedBroadcastTime'])
		li.setProperty('PlayPath', playpath)
		li.setInfo('video', {'title': ep['title'], "plot": ep['description'],
				     'duration': ep['duration']})
		img = baseURL + 'videos/' + str(ep['id']) + '/images/' + imgWidth + 'x' + imgHeight + '.jpg'
		print 'IMG: ' + img
		li.setThumbnailImage(img)
		xbmcplugin.addDirectoryItem(self.handle, url, li, False, self.count)
		return (url, li, False)

	def listEpisodes(self):
		showUrl = self.arg[6:]
		eps = self.getEpisodes(showUrl)
		self.count = len(eps)
		items = map(self.epToItem, eps);
		xbmcplugin.setContent(self.handle, 'episodes')
		# xbmcplugin.addDirectoryItems(self.handle, items, len(items))
		self.endDirs()
		
	def progToDir(self, prog):
		li = xbmcgui.ListItem(prog['title'])
		li.setInfo("video", {"title": prog['title'], 
				     'plot': prog['description']})
		li.setThumbnailImage(baseURL + 'videos/' + str(prog['newestVideoId']) + '/images/' + imgWidth + 'x' + imgHeight + '.jpg')
		return (self.pluginURL+"?show=" + prog['slug'], li, True)

	def listProgs(self):
		progs = self.getProgrammes(baseURL+allURL)		
		dirs = map(self.progToDir, progs)
		xbmcplugin.setContent(self.handle, 'tvshows')
		xbmcplugin.addDirectoryItems(self.handle, dirs, len(dirs))
		self.endDirs(True)

	# def playEpisode(self):
	        # # this method is not used right now
		# epsUrl = self.arg[5:]
		# vurl = self.getVideoURL(Request(epsUrl))
		# parts = vurl.split('mp4:')

		# li = xbmcgui.ListItem(vurl)
		# li.setProperty('PlayPath', 'mp4:' + parts[1])
		# xbmcplugin.setResolvedUrl(self.handle, False, li)
		# #xbmcplugin.addDirectoryItem(self.handle, parts[0], li, False)
		# xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(parts[0], li)
		# # dirs = [(parts[0], li, False)]
		# # xbmcplugin.addDirectoryItems(self.handle, dirs, len(dirs))
		# #self.endDirs()

if (__name__ == "__main__"):
	handle = int(sys.argv[1])
	pluginUrl = sys.argv[0]
	arg = sys.argv[2]
	
	tv = DRtv(handle, pluginUrl, arg)
	del tv

