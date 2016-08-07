import filecmp
import os
import tempfile
from test import helpers
import unittest
import uuid
from genomespaceclient import GSFileMetadata, GSDataFormat
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin


class GenomeSpaceClientTestCase(unittest.TestCase):

    def _get_test_file(self):
        return os.path.join(os.path.dirname(__file__), 'fixtures/logo.png')

    def _get_temp_filename(self):
        return str(uuid.uuid4())

    def _get_temp_file(self):
        return os.path.join(tempfile.gettempdir(), self._get_temp_filename())

    def _get_remote_file(self):
        filename = self._get_temp_filename() + ".txt"
        return (urljoin(helpers.get_remote_test_folder(), filename),
                filename)

    def test_list(self):
        client = helpers.get_genomespace_client()
        local_test_file = self._get_test_file()
        remote_file_path, remote_name = self._get_remote_file()
        client.copy(local_test_file, remote_file_path)
        filelist = client.list(helpers.get_remote_test_folder())
        found_file = [f for f in filelist["contents"]
                      if f["name"] == remote_name]
        self.assertTrue(len(found_file) == 1, "Expected file not found")
        client.delete(remote_file_path)

    def test_copy(self):
        client = helpers.get_genomespace_client()
        local_test_file = self._get_test_file()
        remote_file, _ = self._get_remote_file()
        local_temp_file = self._get_temp_file()

        client.copy(local_test_file, remote_file)
        client.copy(remote_file, local_temp_file)
        client.delete(remote_file)

        self.assertTrue(filecmp.cmp(local_test_file, local_temp_file))
        os.remove(local_temp_file)

    def test_move(self):
        client = helpers.get_genomespace_client()
        local_test_file = self._get_test_file()
        local_temp_file = self._get_temp_file()
        remote_file1, _ = self._get_remote_file()
        remote_file2, _ = self._get_remote_file()

        client.copy(local_test_file, remote_file1)
        client.move(remote_file1, remote_file2)
        client.copy(remote_file2, local_temp_file)
        client.delete(remote_file2)

        filelist = client.list(helpers.get_remote_test_folder())
        found_file = [f for f in filelist["contents"]
                      if f["name"] == remote_file1]
        self.assertTrue(len(found_file) == 0,
                        "File was found but should have been deleted")
        self.assertTrue(filecmp.cmp(local_test_file, local_temp_file))
        os.remove(local_temp_file)

    def test_delete(self):
        client = helpers.get_genomespace_client()
        local_test_file = self._get_test_file()
        remote_file_path, remote_name = self._get_remote_file()
        client.copy(local_test_file, remote_file_path)
        client.delete(remote_file_path)
        filelist = client.list(helpers.get_remote_test_folder())
        found_file = [f for f in filelist["contents"]
                      if f["name"] == remote_name]
        self.assertTrue(len(found_file) == 0,
                        "File was found but should have been deleted")

    def test_get_metadata(self):
        client = helpers.get_genomespace_client()
        local_test_file = self._get_test_file()
        remote_file_path, _ = self._get_remote_file()

        # Set a specific data format
        remote_file_path += '?dataformat=http://www.genomespace.org' \
                            '/datamanager/dataformat/txt'
        client.copy(local_test_file, remote_file_path)
        metadata = client.get_metadata(remote_file_path)
        client.delete(remote_file_path)

        self.assertIsInstance(
            metadata, GSFileMetadata,
            "Expected metadata to be of type GSFileMetadata")
        self.assertIsInstance(
            metadata.dataFormat, GSDataFormat,
            "Expected metadata's dataFormat to be of type GSDataFormat")
        self.assertIsInstance(
            metadata.availableDataFormats, list,
            "Expected metadata's available formats to be of type list")
