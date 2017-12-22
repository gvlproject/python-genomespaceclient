import logging
import os
from abc import ABCMeta, abstractmethod

from cloudbridge.cloud.factory import CloudProviderFactory, ProviderList

from genomespaceclient import util

import requests

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
                              if total_length else "unknown size", end='\r'))
            if log.isEnabledFor(logging.INFO):
                print("\n")


class S3StorageHandler(SimpleStorageHandler):

    def upload(self, source, upload_info):
        creds = upload_info["amazonCredentials"]
        provider = CloudProviderFactory().create_provider(
            ProviderList.AWS,
            {'aws_access_key': creds["accessKey"],
             'aws_secret_key': creds["secretKey"],
             'aws_session_token': creds["sessionToken"]})
        bucket = provider.object_store.get(upload_info['s3BucketName'])
        obj = bucket.create_object(upload_info['s3ObjectKey'])
        obj.upload_from_file(source)


class SwiftStorageHandler(SimpleStorageHandler):
    SEGMENT_SIZE = 2 * 1024 * 1024 * 1024  # 2GB

    def upload(self, source, upload_info):
        container, location = upload_info["path"].split("/", 1)
        provider = CloudProviderFactory().create_provider(
            ProviderList.OPENSTACK,
            {'os_storage_url': upload_info["swiftFileUrl"],
             'os_auth_token': upload_info["token"]})
        bucket = provider.object_store.get(container)
        obj = bucket.create_object(location)
        obj.upload_from_file(source)
