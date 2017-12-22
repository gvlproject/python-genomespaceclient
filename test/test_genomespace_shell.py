import filecmp
import os
import shutil
import tempfile
import unittest
import uuid
from test import helpers

from genomespaceclient import main


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

    def _get_test_folder(self):
        return os.path.join(os.path.dirname(__file__), 'fixtures/')

    def _get_temp_filename(self):
        return str(uuid.uuid4())

    def _get_temp_file(self):
        return os.path.join(tempfile.gettempdir(), self._get_temp_filename())

    def _get_temp_folder(self):
        return tempfile.mkdtemp() + "/"

    def _get_remote_file(self):
        filename = self._get_temp_filename()
        return (urljoin(helpers.get_remote_test_folder(), filename),
                filename)

    def _get_remote_folder(self):
        foldername = self._get_temp_filename()
        return (urljoin(helpers.get_remote_test_folder(), foldername) + "/",
                foldername)

    def test_list(self):
        local_test_file = self._get_test_file()
        remote_file_path, remote_name = self._get_remote_file()

        self._call_shell_command("cp", local_test_file, remote_file_path)
        output = self._call_shell_command(
            "ls", helpers.get_remote_test_folder())
        self.assertTrue(remote_name in output,
                        "Expected file not found. Received: %s" % (output,))
        self._call_shell_command("rm", remote_file_path)

    def test_mkdir_rmdir(self):
        remote_folder, remote_name = self._get_remote_folder()

        self._call_shell_command("mkdir", remote_folder)
        output = self._call_shell_command(
            "ls", helpers.get_remote_test_folder())
        self.assertTrue(remote_name in output,
                        "Expected folder not found. Received: %s" % (output,))

        # The recurse is needed to compensate for a bug in GenomeSpace swift
        # which creates a .hidden file in each folder
        self._call_shell_command("rm", "-R", remote_folder)
        output = self._call_shell_command(
            "ls", helpers.get_remote_test_folder())
        self.assertTrue(
            remote_name not in output,
            "Expected folder to be deleted. Received: %s" % (output,))

    def test_copy(self):
        local_test_file = self._get_test_file()
        local_temp_file = self._get_temp_file()
        remote_file, _ = self._get_remote_file()

        self._call_shell_command("cp", local_test_file, remote_file)
        self._call_shell_command("cp", remote_file, local_temp_file)
        self._call_shell_command("rm", remote_file)

        self.assertTrue(filecmp.cmp(local_test_file, local_temp_file))
        os.remove(local_temp_file)

    def test_copy_folder(self):
        local_test_folder = self._get_test_folder()
        local_temp_folder = self._get_temp_folder()
        remote_folder, _ = self._get_remote_folder()

        self._call_shell_command("mkdir", remote_folder)
        self._call_shell_command("cp", "-R", local_test_folder,
                                 remote_folder)
        self._call_shell_command("cp", "-R", remote_folder, local_temp_folder)
        self._call_shell_command("rm", "-R", remote_folder)

        dcmp = filecmp.dircmp(local_test_folder, local_temp_folder)
        self.assertTrue(len(dcmp.same_files) == 3, "Should have copied 3"
                        " identical files")
        self.assertTrue(len(dcmp.left_only) == 0, "Should have no extra files"
                        " in local fixtures folder")
        self.assertTrue(len(dcmp.right_only) == 0, "Should have no extra files"
                        " in local temp folder")
        self.assertTrue(len(dcmp.subdirs) == 1, "Should have exactly one"
                        " subfolder")
        self.assertTrue(len(dcmp.subdirs['folder1'].common) == 2, "Should have"
                        " exactly 2 files in subfolder")
        self.assertTrue(len(dcmp.subdirs['folder1'].left_only) == 0, "Should"
                        " have no extra files in local subfolder")
        self.assertTrue(len(dcmp.subdirs['folder1'].right_only) == 0, "Should"
                        " have no extra files in copied subfolder")
        shutil.rmtree(local_temp_folder)

    def test_copy_wildcard(self):
        local_test_folder = self._get_test_folder()
        remote_folder, _ = self._get_remote_folder()
        local_temp_folder = self._get_temp_folder()

        self._call_shell_command("mkdir", remote_folder)
        self._call_shell_command("cp", "-R", local_test_folder + "*",
                                 remote_folder)
        self._call_shell_command("cp", "-R", remote_folder + "*.txt",
                                 local_temp_folder)
        self._call_shell_command("rm", "-R", remote_folder)

        dcmp = filecmp.dircmp(local_test_folder, local_temp_folder)
        self.assertTrue(len(dcmp.same_files) == 2, "Should have copied 2"
                        " identical text files")
        self.assertTrue(len(dcmp.left_only) == 2, "Should have 1 extra file"
                        " in local fixtures folder")
        self.assertTrue(len(dcmp.right_only) == 0, "Should have no extra files"
                        " in local temp folder")
        shutil.rmtree(local_temp_folder)

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
                         "File was found but should have been moved")
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

    def test_delete_folder(self):
        local_test_folder = self._get_test_folder()
        remote_folder, remote_name = self._get_remote_folder()

        self._call_shell_command("mkdir", remote_folder)
        self._call_shell_command("cp", "-R", local_test_folder,
                                 remote_folder)
        self._call_shell_command("rm", "-R", remote_folder)

        output = self._call_shell_command(
            "ls", helpers.get_remote_test_folder())
        self.assertTrue(
            remote_name not in output,
            "Expected folder to be deleted. Received: %s" % (output,))

    def test_delete_wildcard(self):
        local_test_folder = self._get_test_folder()
        remote_folder, _ = self._get_remote_folder()

        self._call_shell_command("mkdir", remote_folder)
        self._call_shell_command("cp", local_test_folder + "*",
                                 remote_folder)
        self._call_shell_command("rm", "-R", remote_folder + "*.txt")

        output = self._call_shell_command("ls", remote_folder)
        self.assertTrue('logo.png' in output,
                        "File should not have been deleted")
        self.assertTrue('folder1' in output,
                        "Folder should not have been deleted")
        self._call_shell_command("rm", "-R", remote_folder)
