from __future__ import print_function

from abc import ABCMeta, abstractmethod
import logging
import os

import boto3
from genomespaceclient import util
import requests
import swiftclient.shell


try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


log = logging.getLogger(__name__)


def create_handler(storage_type):
    """
    Factory method to return a storage handler for a particular storage type.
    A storage handler handles uploads/downloads from a storage type (such as
    S3, Swift etc), usually using a relevant native SDK.
    """
    if not storage_type:
        return None
    storage = storage_type.lower()
    if storage == "s3":
        return S3StorageHandler()
    elif storage == "swift":
        return SwiftStorageHandler()
    else:
        return SimpleStorageHandler()


class StorageHandler():

    __metaclass__ = ABCMeta

    @abstractmethod
    def upload(self, source, upload_info):
        pass

    @abstractmethod
    def download(self, download_info, destination):
        pass


class SimpleStorageHandler(StorageHandler):

    def upload(self, source, upload_info):
        raise NotImplementedError(
            "Don't know how to handle upload type: %s" %
            (upload_info.get("uploadType")))

    def download(self, download_info, destination):
        if not destination or os.path.isdir(destination):
            disassembled_uri = urlparse(download_info['Location'])
            filename = os.path.basename(disassembled_uri.path)
            destination = os.path.join(destination, filename)
        with open(destination, 'wb') as handle:
            response = requests.get(download_info['Location'], stream=True)
            response.raise_for_status()
            total_length = response.headers.get('content-length')
            bytes_copied = 0
            for block in response.iter_content(65536):
                handle.write(block)
                bytes_copied += len(block)
                if log.isEnabledFor(logging.INFO):
                    print("Progress: {progress:>8s} of {total:>8s}"
                          " copied".format(
                              progress=util.format_file_size(bytes_copied),
                              total=util.format_file_size(int(total_length))
                              if total_length else "unknown size"),
                          end='\r')
            if log.isEnabledFor(logging.INFO):
                print("\n")


class S3StorageHandler(SimpleStorageHandler):

    def upload(self, source, upload_info):
        creds = upload_info["amazonCredentials"]
        session = boto3.session.Session(
            aws_access_key_id=creds["accessKey"],
            aws_secret_access_key=creds["secretKey"],
            aws_session_token=creds["sessionToken"],
            region_name="us-west-1")
        s3_client = session.client("s3")
        s3_client.upload_file(source,
                              upload_info['s3BucketName'],
                              upload_info['s3ObjectKey'])


class SwiftStorageHandler(SimpleStorageHandler):
    SEGMENT_SIZE = 2 * 1024 * 1024 * 1024  # 2GB

    def upload(self, source, upload_info):
        container, location = upload_info["path"].split("/", 1)
        swiftclient.shell.main(
            ["swift",
             "--os-storage-url", upload_info["swiftFileUrl"],
             "--os-auth-token", upload_info["token"],
             "upload", container,
             "-S", str(SwiftStorageHandler.SEGMENT_SIZE),
             "--segment-container", container,
             "--object-name", location,
             source])
