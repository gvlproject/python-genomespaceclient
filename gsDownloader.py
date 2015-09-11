import gsLogin
from abc import ABCMeta, abstractmethod
import requests.packages.urllib3.util.ssl_
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL'
import shutil
import sys
import argparse

class Downloader:

	#__metaclass__ = ABCMeta
    def requestDownload(self, gsUserName, gsPasword, gsURL, gsDNS, filePath):
        print { 'Cookie' : gsLogin.getGenomeSpaceToken(gsUserName,gsPasword, gsDNS) }
        print "downloading " + gsURL
        r = requests.get(gsURL, stream=True, cookies=gsLogin.getGenomeSpaceToken(gsUserName,gsPasword, gsDNS))
        print { 'Cookie' : gsLogin.getGenomeSpaceToken(gsUserName,gsPasword, gsDNS) }
        with open(filePath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
    def requestDownload(self, gsToken, gsURL, gsDNS, filePath):
        #print { 'Cookie' : gsToken }
        print "downloading " + gsURL
        r = requests.get(gsURL, stream=True, cookies={"gs-token" :gsToken})
        #print { 'Cookie' : gsLogin.getGenomeSpaceToken(gsUserName,gsPasword, gsDNS) }
        with open(filePath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()

def test():
    a = Downloader()
    #a.requestDownload("devtest","devtest", "Home/swift:Demo2/2.lg.txt", "genomespace.genome.edu.au","/Users/yousef/Documents/Uploader2GenomeSpace/gsUploader/ss1.png")
    a.requestDownload("UYEP4NI1gHVOSvXEu+wXR0OozF/Vk1zf", "https://genomespace-dev.genome.edu.au:443/datamanager/file/Home/swift:Demo2/testfile.txt", "genomespace.genome.edu.au","/Users/yousef/Documents/Uploader2GenomeSpace/gsUploader/ss1.png")
def download_file_from_genomespace(server, gsToken, download_url, local_filename):
    a = Downloader()
    a.requestDownload(gsToken, download_url, server,local_filename)
def download_file_from_genomespace(server, user, password, download_url, local_filename):
    a = Downloader()
    a.requestDownload(user, password, download_url, server,local_filename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--server', type=str, help="Genomespace server name", required=True)
    parser.add_argument('-u', '--user', type=str, help="Genomespace username", required=False)
    parser.add_argument('-p', '--password', type=str, help="Genomespace password", required=False)
    parser.add_argument('-d', '--download_url', help="Genomespace URI of file to download", required=True)
    parser.add_argument('-f', '--file', type=str, help="Local filename to save to", required=False, default="output.download")
    parser.add_argument('-n', '--token', help="Genomespace token to talk to GenomeSpace", required=False)
    args = parser.parse_args()
    if len(args.token)>0:
        download_file_from_genomespace(args.server, args.token, args.download_url, args.file)
    else:
        download_file_from_genomespace(args.server, args.user, args.password, args.download_url, args.file)
