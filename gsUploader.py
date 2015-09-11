import gsLogin
from abc import ABCMeta, abstractmethod
import requests.packages.urllib3.util.ssl_
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL'


class Uploader:

	__metaclass__ = ABCMeta

	def requestUpload(self, gsUserName, gsPasword, gsURL, gsDNS):
		print "Uploading: " + gsURL
		r = requests.get(gsURL, cookies = gsLogin.getGenomeSpaceToken(gsUserName,gsPasword, gsDNS), headers = { 'Content-type': 'application/json' })
		return r.text
#
#
# 	def requestUpload(self, gsUserName, gsPasword, gsURL, gsDNS):
# 		opener = urllib2.build_opener(urllib2.HTTPHandler)
# 		request = urllib2.Request(gsURL)
#
# 		request.add_header('Cookie',gsLogin.getGenomeSpaceToken(gsUserName,gsPasword, gsDNS))
#
# 		request.add_header('Content-Type', 'application/json')
# 		try:
# 			resp = opener.open(request)
# 			return resp.read()
# 		except urllib2.HTTPError as e:
# 			print e.read()

	@abstractmethod
	def upload(self, jsnObject, filePath):
		'''This method will recieve jsonObject from genomespace response for requesting a file upload. Each uploader should use the json object to talk t the specific storage type'''
		return


class test(Uploader):

	def upload(self, jsnObject, filePath):
		return

#a = test()
#print a.requestUpload("devtest","devtest", "https://genomespace-dev.genome.edu.au/datamanager/v1.0/uploadinfo/Home/swift:Demo2/test1.png", "genomespace.genome.edu.au")