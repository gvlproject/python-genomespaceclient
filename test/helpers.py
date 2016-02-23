import os
from genomespaceclient import GenomeSpaceClient


def get_test_username():
    return os.environ["GENOMESPACE_USERNAME"]


def get_test_password():
    return os.environ["GENOMESPACE_PASSWORD"]


def get_genomespace_client():
    return GenomeSpaceClient(username=get_test_username(),
                             password=get_test_password())


def get_test_folder():
    return os.environ["GENOMESPACE_TEST_FOLDER"]
