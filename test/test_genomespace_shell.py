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

    def _get_temp_filename(self):
        return str(uuid.uuid4())

    def _get_temp_file(self):
        return os.path.join(tempfile.gettempdir(), self._get_temp_filename())

    def _get_remote_file(self):
        filename = self._get_temp_filename()
        return (urljoin(helpers.get_remote_test_folder(), filename),
                filename)

    def test_list(self):
        local_test_file = self._get_test_file()
        remote_file_path, remote_name = self._get_remote_file()

        self._call_shell_command("cp", local_test_file, remote_file_path)
        output = self._call_shell_command(
            "ls", helpers.get_remote_test_folder())
        self.assertTrue(remote_name in output,
                        "Expected file not found. Received: %s" % (output,))
        self._call_shell_command("rm", remote_file_path)

    def test_copy(self):
        local_test_file = self._get_test_file()
        local_temp_file = self._get_temp_file()
        remote_file, _ = self._get_remote_file()

        self._call_shell_command("cp", local_test_file, remote_file)
        self._call_shell_command("cp", remote_file, local_temp_file)
        self._call_shell_command("rm", remote_file)

        self.assertTrue(filecmp.cmp(local_test_file, local_temp_file))
        os.remove(local_temp_file)

    def test_encoded_copy(self):
        local_test_file = self._get_test_file()
        local_temp_file = self._get_temp_file()
        remote_file, _ = self._get_remote_file()

        source = binascii.hexlify(local_test_file.encode("utf8"))
        remote_target = binascii.hexlify(remote_file.encode("utf8"))
        local_target = binascii.hexlify(local_temp_file.encode("utf8"))
        self._call_shell_command("encoded_cp", source.decode("ascii"),
                                 remote_target.decode("ascii"))
        self._call_shell_command("encoded_cp", remote_target.decode("ascii"),
                                 local_target.decode("ascii"))
        self._call_shell_command("rm", remote_file)

        self.assertTrue(filecmp.cmp(local_test_file, local_temp_file))
        os.remove(local_temp_file)

    def test_move(self):
        local_test_file = self._get_test_file()
        local_temp_file = self._get_temp_file()
        remote_file1, _ = self._get_remote_file()
        remote_file2, _ = self._get_remote_file()

        self._call_shell_command("cp", local_test_file, remote_file1)
        self._call_shell_command("mv", remote_file1, remote_file2)
        self._call_shell_command("cp", remote_file2, local_temp_file)
        self._call_shell_command("rm", remote_file2)

        output = self._call_shell_command(
            "ls", helpers.get_remote_test_folder())
        self.assertFalse(remote_file1 in output,
                         "File was found but should have been deleted")
        self.assertTrue(filecmp.cmp(local_test_file, local_temp_file))
        os.remove(local_temp_file)

    def test_delete(self):
        local_test_file = self._get_test_file()
        remote_file_path, remote_name = self._get_remote_file()

        self._call_shell_command("cp", local_test_file, remote_file_path)
        self._call_shell_command("rm", remote_file_path)

        output = self._call_shell_command(
            "ls", helpers.get_remote_test_folder())
        self.assertFalse(remote_name in output,
                         "File was found but should have been deleted")
