import os
from genomespaceclient import GenomeSpaceClient


def get_genomespace_client():
    return GenomeSpaceClient(os.environ["GENOMESPACE_USERNAME"],
                             os.environ["GENOMESPACE_PASSWORD"])


def get_test_folder():
    return os.environ["GENOMESPACE_TEST_FOLDER"]
