import filecmp
import os
import tempfile
from test import helpers
import unittest
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin
from genomespaceclient import main


class GenomeSpaceShellTestCase(unittest.TestCase):

    def _call_shell_command(self, command, *args):
        main_args = ["genomespace", "-u", helpers.get_test_username(),
                     "-p", helpers.get_test_password(),
                     command]
        main(main_args + list(args))

    def _get_test_file(self):
        return os.path.join(os.path.dirname(__file__), 'fixtures/logo.png')

    def _get_temp_file(self):
        return os.path.join(tempfile.gettempdir(), 'logo_temp.png')

    def test_list(self):
        local_test_file = self._get_test_file()

        self._call_shell_command(
            "cp", local_test_file,
            urljoin(helpers.get_test_folder(), 'list_logo.png'))
        self._call_shell_command(
            "ls", helpers.get_test_folder())
        # self.assertTrue(len(found_file) == 1, "Expected file not found")

    def test_copy(self):
        local_test_file = self._get_test_file()
        local_temp_file = self._get_temp_file()
        if os.path.exists(local_temp_file):
            os.remove(local_temp_file)

        self._call_shell_command(
            "cp", local_test_file,
            urljoin(helpers.get_test_folder(), 'logo.png'))

        self._call_shell_command(
            "cp", urljoin(helpers.get_test_folder(), 'logo.png'),
            local_temp_file)

        self.assertTrue(filecmp.cmp(local_test_file, local_temp_file))
        os.remove(local_temp_file)

    def test_move(self):
        local_test_file = self._get_test_file()
        local_temp_file = self._get_temp_file()

        client = helpers.get_genomespace_client()
        filelist = client.list(helpers.get_test_folder())
        found_file = [f for f in filelist["contents"]
                      if f["name"] == "logo_copy.png"]
        if len(found_file) == 1:
            client.delete(urljoin(helpers.get_test_folder(), 'logo_copy.png'))

        self._call_shell_command(
            "cp", local_test_file,
            urljoin(helpers.get_test_folder(), 'logo.png'))

        self._call_shell_command(
            "mv", urljoin(helpers.get_test_folder(), 'logo.png'),
            urljoin(helpers.get_test_folder(), 'logo_copy.png'))

        self._call_shell_command(
            "cp", urljoin(helpers.get_test_folder(), 'logo_copy.png'),
            local_temp_file)

        self.assertTrue(filecmp.cmp(local_test_file, local_temp_file))
        os.remove(local_temp_file)

    def test_delete(self):
        local_test_file = self._get_test_file()
        self._call_shell_command(
            "cp", local_test_file,
            urljoin(helpers.get_test_folder(), 'delete_logo.png'))
        self._call_shell_command(
            "rm", urljoin(helpers.get_test_folder(), 'delete_logo.png'))
