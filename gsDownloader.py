import gsLogin
from abc import ABCMeta, abstractmethod
import  urllib2
import shutil
import sys

class Downloader:
    
	#__metaclass__ = ABCMeta
	def requestDownload(self, gsUserName, gsPasword, gsURL, gsDNS, filePath):
		opener = urllib2.build_opener(urllib2.HTTPHandler)
		request = urllib2.Request(gsURL)
		
		request.add_header('Cookie',gsLogin.getGenomeSpaceToken(gsUserName,gsPasword, gsDNS))
        
		#request.add_header('Content-Type', 'application/json')
		try:
			resp = opener.open(request)
			print "downloading " + gsURL

			# Open our local file for writing
			with open(filePath, "wb") as local_file:
				shutil.copyfileobj(resp,local_file)
				print "Finished."
                
			return
		except urllib2.HTTPError as e:
			print e.read()

if __name__ == "__main__":
    objectUrl = ""
    gsUser = ""
    gsPSW = ""
    filePath = ""
    gsDNS = ""
    index = 1
    while(index<len(sys.argv)):
        #print sys.argv[index]
        if sys.argv[index]=="url":
            objectUrl = sys.argv[index+1]
            index+=2
        elif sys.argv[index]=="user":
            gsUser = sys.argv[index+1]
            index+=2
        elif sys.argv[index]=="psw":
            gsPSW = sys.argv[index+1]
            index+=2
        elif sys.argv[index]=="file":
            filePath = sys.argv[index+1]
            index+=2
        elif sys.argv[index]=="genomespace":
            gsDNS = sys.argv[index+1]
            index+=2
        else:
            index+=1
    objectUrl = "https://"+gsDNS+"/datamanager/file/" + objectUrl
    d = Downloader()
    d.requestDownload(gsUser,gsPSW, objectUrl, gsDNS, filePath)

def test():
    a = Downloader()
    a.requestDownload("devtest","devtest", "Home/swift:Demo2/2.lg.txt", "genomespace.genome.edu.au","/Users/yousef/Documents/Uploader2GenomeSpace/gsUploader/ss1.png")

