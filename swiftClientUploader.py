from gsUploader import *
import ast
import os
import sys
import requests.packages.urllib3.util.ssl_
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL'

import swiftclient.shell
import traceback
class swiftUploader(Uploader):
    CHUNK_SIZE = 1024*1024*1024 #1Gig
    def upload(self, jsnObject, filePath):
        try:
            
            jsonDic = ast.literal_eval(jsnObject)
            if(jsonDic["uploadType"]!="Swift"):
                print jsonDic
                raise ValueError("Not a Swift storage.")
            url =jsonDic["swiftFileUrl"]+"/"+jsonDic["path"]
            
            url = url.replace("\\","")
            parts = url.split("/")
            index = 0
            for s in parts:
                index+=1
                if "AUTH" in s:
                    break;
            container = parts[index]
            storagePath = "/".join(parts[0:index])
            urlPath = "/".join(parts[index+1:])


            token = jsonDic["token"]
#, "--segment-container", container
            swiftclient.shell.main(["swift", "--os-storage-url", storagePath, "--os-auth-token", token, "upload", container, "-S", str(self.CHUNK_SIZE),"--object-threads", "10", "--segment-container", container, "--object-name", urlPath, filePath])
                #sys.exit()
        except:
            return sys.exit(traceback.format_exc())


