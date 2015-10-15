from gsUploader import *
import ast
import os
import sys
import requests.packages.urllib3.util.ssl_
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL'
import argparse
import swiftclient.shell
import traceback
class swiftUploader(Uploader):
    CHUNK_SIZE = 1024*1024*1024 #1Gig
    def swiftClientUploader(self, jsnObject, filePath):
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


def upload_file_to_genomespace_bytoken(server, gsToken, target_url, local_filename):
    uploader = swiftUploader()
    upload_request = uploader.requestUpload(gsToken, target_url.replace("/datamanager/v1.0/file/", "/datamanager/v1.0/uploadinfo/"), server)
    uploader.swiftClientUploader(upload_request, local_filename)

def upload_file_to_genomespace_byswiftCleint(server, gsToken, target_url, local_filename):
    uploader = swiftUploader()
    upload_request = uploader.requestUpload(gsToken, target_url.replace("/datamanager/v1.0/file/", "/datamanager/v1.0/uploadinfo/"), server)
    uploader.swiftClientUploader(upload_request, local_filename)

def upload_file_to_genomespace(server, user, password, target_url, local_filename):
    uploader = swiftUploader()
    upload_request = uploader.requestUpload(user, password, target_url.replace("/datamanager/v1.0/file/", "/datamanager/v1.0/uploadinfo/"), server)
    uploader.swiftClientUploader(upload_request, local_filename)

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
        upload_file_to_genomespace_bytoken(args.server, args.token, args.target_url, args.file)
    else:
        upload_file_to_genomespace(args.server, args.user, args.password, args.target_url, args.file)