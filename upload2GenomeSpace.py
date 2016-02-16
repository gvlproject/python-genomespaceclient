import argparse
from uploadFactory import uploadFactory, Uploader
import re

def upload_file_to_genomespace_bytoken(server, gsToken, target_url, local_filename):
    typeReg =re.search('(?<=Home.)\w+', a)
    uploaderType = typeReg.group(0)
    uploader = uploadFactory.getUploader(uploaderType)
    upload_request = uploader.requestUpload(gsToken, target_url.replace("/datamanager/v1.0/file/", "/datamanager/v1.0/uploadinfo/"), server)
    uploader.upload(upload_request, local_filename)

#def upload_file_to_genomespace_byswiftCleint(server, gsToken, target_url, local_filename):
#    uploaderType = ""
#    uploader = uploadFactory.getUploader(uploaderType)
#    upload_request = uploader.requestUpload(gsToken, target_url.replace("/datamanager/v1.0/file/", "/datamanager/v1.0/uploadinfo/"), server)
#    uploader.upload(upload_request, local_filename)

def upload_file_to_genomespace(server, user, password, target_url, local_filename):
    typeReg =re.search('(?<=Home.)\w+', a)
    uploaderType = typeReg.group(0)
    uploader = uploadFactory.getUploader(uploaderType)
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
        upload_file_to_genomespace_bytoken(args.server, args.token, args.target_url, args.file)
    else:
        upload_file_to_genomespace(args.server, args.user, args.password, args.target_url, args.file)#a = test()
