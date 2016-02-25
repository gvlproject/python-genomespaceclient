import filecmp
import os
import tempfile
from test import helpers
import unittest
import uuid

from genomespaceclient import main
import binascii


try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin


class GenomeSpaceShellTestCase(unittest.TestCase):

    def _call_shell_command(self, command, *args):
        main_args = ["genomespace", "-u", helpers.get_test_username(),
                     "-p", helpers.get_test_password(),
                     command] + list(args)

        return helpers.run_python_script(main, main_args)

    def _get_test_file(self):
        return os.path.join(os.path.dirname(__file__), 'fixtures/logo.png')

    def _get_temp_file(self):
        return os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))

    def test_list(self):
        local_test_file = self._get_test_file()

        self._call_shell_command(
            "cp", local_test_file,
            urljoin(helpers.get_test_folder(), 'list_logo.png'))
        output = self._call_shell_command(
            "ls", helpers.get_test_folder())
        self.assertTrue(
            'list_logo.png' in output,
            "Expected file not found. Received: %s" %
            (output,))

    def test_copy(self):
        local_test_file = self._get_test_file()
        local_temp_file = self._get_temp_file()

        self._call_shell_command(
            "cp", local_test_file,
            urljoin(helpers.get_test_folder(), 'logo.png'))

        self._call_shell_command(
            "cp", urljoin(helpers.get_test_folder(), 'logo.png'),
            local_temp_file)

        self.assertTrue(filecmp.cmp(local_test_file, local_temp_file))
        os.remove(local_temp_file)

    def test_encoded_copy(self):
        local_test_file = self._get_test_file()
        local_temp_file = self._get_temp_file()

        source = binascii.hexlify(local_test_file.encode("utf8"))
        remote_target = binascii.hexlify(
            urljoin(helpers.get_test_folder(), 'logo.png').encode("utf8"))
        local_target = binascii.hexlify(local_temp_file.encode("utf8"))
        self._call_shell_command("encoded_cp", source.decode("ascii"),
                                 remote_target.decode("ascii"))

        self._call_shell_command("encoded_cp", remote_target.decode("ascii"),
                                 local_target.decode("ascii"))

        self.assertTrue(filecmp.cmp(local_test_file, local_temp_file))
        os.remove(local_temp_file)

    def test_move(self):
        local_test_file = self._get_test_file()
        local_temp_file = self._get_temp_file()

        output = self._call_shell_command(
            "ls", helpers.get_test_folder())
        if 'list_logo.png' in output:
            self._call_shell_command(
                "rm", urljoin(helpers.get_test_folder(), 'logo_copy.png'))

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
