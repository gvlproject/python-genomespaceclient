import filecmp
import os
import tempfile
from test import helpers
import unittest
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin


class GenomeSpaceClientTestCase(unittest.TestCase):

    def _get_test_file(self):
        return os.path.join(os.path.dirname(__file__), 'fixtures/logo.png')

    def _get_temp_file(self):
        return os.path.join(tempfile.gettempdir(), 'logo_temp.png')

    def test_list(self):
        client = helpers.get_genomespace_client()
        local_test_file = self._get_test_file()
        client.copy(local_test_file,
                    urljoin(helpers.get_test_folder(), 'list_logo.png'))
        filelist = client.list(helpers.get_test_folder())
        found_file = [f for f in filelist["contents"]
                      if f["name"] == "list_logo.png"]
        self.assertTrue(len(found_file) == 1, "Expected file not found")

    def test_copy(self):
        client = helpers.get_genomespace_client()
        local_test_file = self._get_test_file()
        local_temp_file = self._get_temp_file()
        if os.path.exists(local_temp_file):
            os.remove(local_temp_file)
        client.copy(local_test_file,
                    urljoin(helpers.get_test_folder(), 'logo.png'))
        client.copy(urljoin(helpers.get_test_folder(), 'logo.png'),
                    local_temp_file)
        self.assertTrue(filecmp.cmp(local_test_file, local_temp_file))
        os.remove(local_temp_file)

    def test_move(self):
        client = helpers.get_genomespace_client()
        local_test_file = self._get_test_file()
        local_temp_file = self._get_temp_file()
        filelist = client.list(helpers.get_test_folder())
        found_file = [f for f in filelist["contents"]
                      if f["name"] == "logo_copy.png"]
        if len(found_file) == 1:
            client.delete(urljoin(helpers.get_test_folder(), 'logo_copy.png'))
        client.copy(local_test_file,
                    urljoin(helpers.get_test_folder(), 'logo.png'))
        client.move(urljoin(helpers.get_test_folder(), 'logo.png'),
                    urljoin(helpers.get_test_folder(), 'logo_copy.png'),)
        client.copy(urljoin(helpers.get_test_folder(), 'logo_copy.png'),
                    local_temp_file)
        self.assertTrue(filecmp.cmp(local_test_file, local_temp_file))
        os.remove(local_temp_file)

    def test_delete(self):
        client = helpers.get_genomespace_client()
        local_test_file = self._get_test_file()
        client.copy(local_test_file,
                    urljoin(helpers.get_test_folder(), 'delete_logo.png'))
        client.delete(urljoin(helpers.get_test_folder(), 'delete_logo.png'))
        filelist = client.list(helpers.get_test_folder())
        found_file = [f for f in filelist["contents"]
                      if f["name"] == "delete_logo.png"]
        self.assertTrue(len(found_file) == 0,
                        "File was found should have been deleted")
