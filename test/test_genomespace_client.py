import filecmp
import os
import shutil
import tempfile
import unittest
import uuid
from test import helpers
from test.helpers import get_test_username

from genomespaceclient import GSDataFormat, GSFileMetadata

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin


class GenomeSpaceClientTestCase(unittest.TestCase):

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
        filename = self._get_temp_filename() + ".txt"
        return (urljoin(helpers.get_remote_test_folder(), filename),
                filename)

    def _get_remote_folder(self):
        foldername = self._get_temp_filename()
        return (urljoin(helpers.get_remote_test_folder(), foldername) + "/",
                foldername)

    def _adjust_gs_swift_bug(self, name):
        """
        GenomeSpace Swift adds a / to the end of a foldername in metadata.
        Remove that /
        """
        if name:
            return name.replace("/", "")
        else:
            return name

    def test_list(self):
        client = helpers.get_genomespace_client()
        local_test_file = self._get_test_file()
        remote_file_path, remote_name = self._get_remote_file()
        client.copy(local_test_file, remote_file_path)
        filelist = client.list(helpers.get_remote_test_folder())
        found_file = [f for f in filelist.contents
                      if f.name == remote_name]
        self.assertTrue(len(found_file) == 1, "Expected file not found")
        client.delete(remote_file_path)

    def test_mkdir_rmdir(self):
        client = helpers.get_genomespace_client()
        remote_folder1, remote_name1 = self._get_remote_folder()
        client.mkdir(remote_folder1)
        filelist = client.list(helpers.get_remote_test_folder())
        found_file = [f for f in filelist.contents
                      if self._adjust_gs_swift_bug(f.name) == remote_name1 and
                      f.is_directory]
        self.assertTrue(len(found_file) == 1,
                        "Expected to find one created folder")
        # The recurse is needed to compensate for a bug in GenomeSpace swift
        # which creates a .hidden file in each folder
        client.delete(remote_folder1, recurse=True)
        filelist = client.list(helpers.get_remote_test_folder())
        found_file = [f for f in filelist.contents
                      if self._adjust_gs_swift_bug(f.name) == remote_name1]
        self.assertTrue(len(found_file) == 0,
                        "Expected folder to be deleted but it's not")

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

    def test_copy_wildcard(self):
        client = helpers.get_genomespace_client()
        local_test_folder = self._get_test_folder()
        remote_folder, _ = self._get_remote_folder()
        local_temp_folder = self._get_temp_folder()

        client.mkdir(remote_folder)
        client.copy(local_test_folder + "*", remote_folder)
        client.copy(remote_folder + "*.txt", local_temp_folder)
        client.delete(remote_folder, recurse=True)

        dcmp = filecmp.dircmp(local_test_folder, local_temp_folder)
        self.assertTrue(len(dcmp.same_files) == 2, "Should have copied 2"
                        " identical text files")
        self.assertTrue(len(dcmp.left_only) == 2, "Should have 1 extra file"
                        " in local fixtures folder")
        self.assertTrue(len(dcmp.right_only) == 0, "Should have no extra files"
                        " in local temp folder")
        shutil.rmtree(local_temp_folder)

    def test_copy_folder(self):
        client = helpers.get_genomespace_client()
        local_test_folder = self._get_test_folder()
        remote_folder, _ = self._get_remote_folder()
        local_temp_folder = self._get_temp_folder()

        client.mkdir(remote_folder)
        client.copy(local_test_folder, remote_folder, recurse=True)
        client.copy(remote_folder, local_temp_folder, recurse=True)
        client.delete(remote_folder, recurse=True)

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

    def test_move(self):
        client = helpers.get_genomespace_client()
        local_test_file = self._get_test_file()
        local_temp_file = self._get_temp_file()
        remote_file1, remote_name1 = self._get_remote_file()
        remote_file2, _ = self._get_remote_file()

        client.copy(local_test_file, remote_file1)
        client.move(remote_file1, remote_file2)
        client.copy(remote_file2, local_temp_file)
        client.delete(remote_file2)

        filelist = client.list(helpers.get_remote_test_folder())
        found_file = [f for f in filelist.contents
                      if f.name == remote_name1]
        self.assertTrue(len(found_file) == 0,
                        "File was found but should have been moved")
        self.assertTrue(filecmp.cmp(local_test_file, local_temp_file))
        os.remove(local_temp_file)

    def test_move_wildcard(self):
        client = helpers.get_genomespace_client()
        local_test_folder = self._get_test_folder()
        local_temp_folder = self._get_temp_folder()
        remote_folder1, _ = self._get_remote_folder()
        remote_folder2, _ = self._get_remote_folder()

        client.mkdir(remote_folder1)
        client.mkdir(remote_folder2)
        client.copy(local_test_folder + "*", remote_folder1)
        client.move(remote_folder1 + "*.txt", remote_folder2)
        client.copy(remote_folder2 + "*", local_temp_folder)
        client.delete(remote_folder1, recurse=True)
        client.delete(remote_folder2, recurse=True)

        dcmp = filecmp.dircmp(local_test_folder, local_temp_folder)
        self.assertTrue(len(dcmp.same_files) == 2, "Should have copied 2"
                        " identical text files")
        self.assertTrue(len(dcmp.left_only) == 2, "Should have 2 extra files"
                        " in local fixtures folder")
        self.assertTrue(len(dcmp.right_only) == 0, "Should have no extra files"
                        " in local temp folder")
        shutil.rmtree(local_temp_folder)

    def test_delete(self):
        client = helpers.get_genomespace_client()
        local_test_file = self._get_test_file()
        remote_file_path, remote_name = self._get_remote_file()
        client.copy(local_test_file, remote_file_path)
        client.delete(remote_file_path)
        filelist = client.list(helpers.get_remote_test_folder())
        found_file = [f for f in filelist.contents
                      if f.name == remote_name]
        self.assertTrue(len(found_file) == 0,
                        "File was found but should have been deleted")

    def test_delete_folder(self):
        client = helpers.get_genomespace_client()
        local_test_folder = self._get_test_folder()
        remote_folder, remote_name = self._get_remote_folder()

        client.mkdir(remote_folder)
        client.copy(local_test_folder, remote_folder, recurse=True)
        client.delete(remote_folder, recurse=True)

        filelist = client.list(helpers.get_remote_test_folder())
        found_folder = [f for f in filelist.contents
                        if self._adjust_gs_swift_bug(f.name) == remote_name]
        self.assertTrue(len(found_folder) == 0,
                        "Folder was found but should have been deleted")

    def test_delete_wildcard(self):
        client = helpers.get_genomespace_client()
        local_test_folder = self._get_test_folder()
        remote_folder, _ = self._get_remote_folder()

        client.mkdir(remote_folder)
        client.copy(local_test_folder + "*", remote_folder)
        client.delete(remote_folder + "*.txt")
        filelist = client.list(remote_folder)
        found_file = [f for f in filelist.contents]
        self.assertTrue(len(found_file) == 2,
                        "Two items should be remaining but found: %s"
                        % (found_file,))
        client.delete(remote_folder, recurse=True)

    def test_get_metadata(self):
        client = helpers.get_genomespace_client()
        local_test_file = self._get_test_file()
        remote_file_path, remote_name = self._get_remote_file()

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
            metadata.data_format, GSDataFormat,
            "Expected metadata's dataFormat to be of type GSDataFormat")
        self.assertIsInstance(
            metadata.available_data_formats, list,
            "Expected metadata's available formats to be of type list")

        owner = get_test_username()
        self.assertTrue(
            metadata.owner['name'] == owner,
            "Expected file to owned by uploader")
        acl_object = metadata.effective_acl.object
        self.assertTrue(
            acl_object.object_id.endswith(remote_name),
            "Expected acl object path of %s to end with %s" % (
                acl_object.object_id, remote_name))
        self.assertTrue(
            acl_object.object_type == 'DataManagerFileObject',
            "Expected acl object type has changed?")
        access_control_entries = metadata.effective_acl.access_control_entries
        self.assertTrue(
            len(access_control_entries) == 2,
            "Expected only two entries in ACL")
        self.assertTrue(
            access_control_entries[0].permission in ('W', 'R'),
            "Expected owner to be able to read or write file?")
        self.assertTrue(
            access_control_entries[0].sid.type in ('User', 'Group'),
            "Expected sid type to be either 'User' or 'Group'")
        self.assertTrue(
            access_control_entries[0].sid.name == owner,
            "Expected sid name to be the owner")

    def test_get_token_expiry(self):
        client = helpers.get_genomespace_client()
        genomespace_url = helpers.get_genomespace_url()
        # no gs-token, as have not yet performed any actions
        milliseconds_left = client.get_remaining_token_time(genomespace_url)
        self.assertTrue(
            milliseconds_left == 0,
            "Expected client not yet logged in to have no token expiry time")
        # now force a login and hence the client to get a gs-token
        client.list(helpers.get_remote_test_folder())
        milliseconds_left = client.get_remaining_token_time(genomespace_url)
        self.assertTrue(
            milliseconds_left > 0,
            "Expected a logged in client to have a token expiry time")
