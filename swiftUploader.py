from gsUploader import *
import ast
import os
import sys


class swiftUploader(Uploader):
    
    CHUNK_SIZE = 64*1024*1024
    def upload(self, jsnObject, filePath):
        jsonDic = ast.literal_eval(jsnObject)
        if(jsonDic["uploadType"]!="Swift"):
            print jsonDic
            return 0
        url =jsonDic["swiftFileUrl"]+"/"+jsonDic["path"]
        url = url.replace("\\","")
        token = jsonDic["token"]
        size = os.path.getsize(filePath)
        file  = open(filePath, "rb")
        if(size <= self.CHUNK_SIZE):
            bytes = file.read()
            self.uploadFile(url, token, bytes)
        else:
            index = 0
            readsize = 0
            while(readsize<size):
                bytes = file.read(self.CHUNK_SIZE);
                readsize += len(bytes);
                self.uploadFile(url+"_gs_segments/"+self.generateSortedNumberString(index), token, bytes)
                index+=1
            segPath = jsonDic["path"].replace("\\","") +"_gs_segments/"
            print segPath
            self.uploadManifest(url,segPath,token)
        file.close()

    def uploadFile(self, url, token, bytes):
        
        
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(url, data=bytes)
        request.add_header('X-Auth-Token', token)
        request.add_header('Content-Length',len(bytes))
        request.get_method = lambda: 'PUT'
        try:
            resp = opener.open(request)
            resp.read()
            print "Chunk " + url + "uploaded"
        except urllib2.HTTPError as e:
            print e.read()
    def uploadManifest(self, url, segmentPath, token):
        bytes = "1"
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(url, data=bytes)
        request.add_header('X-Auth-Token', token)
        request.add_header('Content-Length',1)
        request.add_header('X-Object-Manifest', segmentPath)
        request.get_method = lambda: 'PUT'
        try:
            resp = opener.open(request)
            print resp.read()
        except urllib2.HTTPError as e:
            print e.read()
    def generateSortedNumberString(self, num):
        if num < 10:
            return str(num)
        retVal = '-' + str(num)
        prefix = ''
        numStr = str(num);
        while (len(numStr) > 1):
            numStr = str(len(numStr))
            prefix += 'A'
            retVal = numStr + retVal

        return prefix + retVal;

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
    urlPart = objectUrl[objectUrl.index("Home"):]
    objectUrl = "https://"+gsDNS+"/datamanager/v1.0/uploadinfo/"+urlPart
    u = swiftUploader()
    upJsn = u.requestUpload(gsUser,gsPSW, objectUrl, gsDNS)
    u.upload(upJsn, filePath)
#u = swiftUploader()

#upJsn = u.requestUpload("devtest","devtest", "Home/swift:Demo2/1.lg.txt")
#u.upload(upJsn, "/Users/yousef/Documents/largefiles/1.lg.txt")