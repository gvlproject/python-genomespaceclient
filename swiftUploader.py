from gsUploader import *
import ast
import os
import sys
import requests.packages.urllib3.util.ssl_
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL'
import argparse

'''
    THIS CLASS IS AN OLD WAY TO UPLOAD TO GENOMESPACE WE REPLACED IT WITH SWIFTCLIENTUPLOADER. SEE THE IMPLEMENTATION INSIDE swiftClientUploader.py
    '''

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
        r = requests.put(url, headers = { 'X-Auth-Token' : token, 'Content-Length': len(bytes) }, data=bytes)
        print "Chunk " + url + "uploaded"
#         opener = urllib2.build_opener(urllib2.HTTPHandler)
#         request = urllib2.Request(url, data=bytes)
#         request.add_header('X-Auth-Token', token)
#         request.add_header('Content-Length',len(bytes))
#         request.get_method = lambda: 'PUT'
#         try:
#             resp = opener.open(request)
#             resp.read()
#             print "Chunk " + url + "uploaded"
#         except urllib2.HTTPError as e:
#             print e.read()

    def uploadManifest(self, url, segmentPath, token):
        bytes = "1"
        r = requests.put(url, headers = { 'X-Auth-Token' : token, 'Content-Length': len(bytes), 'X-Object-Manifest' : segmentPath }, data=bytes)

#         opener = urllib2.build_opener(urllib2.HTTPHandler)
#         request = urllib2.Request(url, data=bytes)
#         request.add_header('X-Auth-Token', token)
#         request.add_header('Content-Length',1)
#         request.add_header('X-Object-Manifest', segmentPath)
#         request.get_method = lambda: 'PUT'
#         try:
#             resp = opener.open(request)
#             print resp.read()
#         except urllib2.HTTPError as e:
#             print e.read()
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

#u = swiftUploader()

#upJsn = u.requestUpload("devtest","devtest", "Home/swift:Demo2/1.lg.txt")
#u.upload(upJsn, "/Users/yousef/Documents/largefiles/1.lg.txt")
def upload_file_to_genomespace_bytoken(server, gsToken, target_url, local_filename):
    uploader = swiftUploader()
    upload_request = uploader.requestUpload(gsToken, target_url.replace("/datamanager/v1.0/file/", "/datamanager/v1.0/uploadinfo/"), server)
    uploader.upload(upload_request, local_filename)

def upload_file_to_genomespace(server, user, password, target_url, local_filename):
    uploader = swiftUploader()
    upload_request = uploader.requestUpload(user, password, target_url.replace("/datamanager/v1.0/file/", "/datamanager/v1.0/uploadinfo/"), server)
    uploader.upload(upload_request, local_filename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--server', type=str, help="Genomespace server name", required=True)
    parser.add_argument('-u', '--user', type=str, help="Genomespace username", required=False)
    parser.add_argument('-p', '--password', type=str, help="Genomespace password", required=False)
    parser.add_argument('-t', '--target_url', help="Genomespace target URI of file to upload", required=True)
    parser.add_argument('-f', '--file', type=str, help="Local file to upload", required=True)
    parser.add_argument('-n', '--token', type=str, help="GenomeSpace valid token to talk to GenomeSpace", required=False)
    args = parser.parse_args()
    if len(args.token)>0:
        upload_file_to_genomespace(args.server, args.token, args.target_url, args.file)
    else:
        upload_file_to_genomespace(args.server, args.user, args.password, args.target_url, args.file)






















