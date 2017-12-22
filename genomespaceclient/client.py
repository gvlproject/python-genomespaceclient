import errno
import glob
import logging
import os
import re

from genomespaceclient import gs_glob
from genomespaceclient import storage_handlers
from genomespaceclient.exceptions import GSClientException

import requests
from requests.exceptions import HTTPError

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


log = logging.getLogger(__name__)


class GSDataFormat(object):
    """
    See: http://www.genomespace.org/support/api/restful-access-to-dm#appendix_c
    """

    def __init__(self, name, url, file_extension, description):
        self.name = name
        self.url = url
        self.file_extension = file_extension
        self.description = description

    @staticmethod
    def from_json(json_data):
        if json_data:
            return GSDataFormat(
                json_data.get('name'),
                json_data.get('url'),
                json_data.get('fileExtension'),
                json_data.get('description')
            )
        else:
            return None


class GSSidObject(object):
    """
    See: http://www.genomespace.org/support/api/restful-access-to-dm#sid
    """

    def __init__(self, name, sid_type, sid_id=None):
        self.name = name
        self.type = sid_type
        self.id = sid_id

    @staticmethod
    def from_json(json_data):
        if json_data:
            return GSSidObject(
                json_data.get('name'),
                json_data.get('type'),
                json_data.get('id'),
            )
        else:
            return None


class GSAceObject(object):
    """
    See: http://www.genomespace.org/support/api/restful-access-to-dm#ace
    """

    def __init__(self, permission, sid, ace_id=None):
        self.permission = permission
        self.sid = sid
        self.id = ace_id

    @staticmethod
    def from_json(json_data):
        if json_data:
            return GSAceObject(
                json_data.get('permission'),
                GSSidObject.from_json(json_data.get('sid')),
                json_data.get('id'),
            )
        else:
            return None


class GSAclObject(object):
    """
    See: http://www.genomespace.org/support/api/restful-access-to-dm#acl
    """

    def __init__(self, object_id, object_type):
        self.object_id = object_id
        self.object_type = object_type

    @staticmethod
    def from_json(json_data):
        if json_data:
            return GSAclObject(
                json_data.get('objectId'),
                json_data.get('objectType'),
            )
        else:
            return None


class GSEffectiveAcl(object):
    """
    See: http://www.genomespace.org/support/api/restful-access-to-dm#appendix_f
    """

    def __init__(self, access_control_entries, effective_acl_object,
                 effective_acl_id=None):
        self.access_control_entries = access_control_entries
        self.object = effective_acl_object
        self.id = effective_acl_id

    @staticmethod
    def from_json(json_data):
        if json_data:
            return GSEffectiveAcl(
                [GSAceObject.from_json(entry) for entry in
                 json_data.get('accessControlEntries')],
                GSAclObject.from_json(json_data.get('object')),
                json_data.get('id'),
            )
        else:
            return None


class GSFileMetadata(object):
    """
    See: http://www.genomespace.org/support/api/restful-access-to-dm#appendix_a
    """

    def __init__(self, name, path, url, parentUrl, size, owner, is_directory,
                 is_link, target_path, last_modified, data_format,
                 available_data_formats, effective_acl):
        self.name = name
        self.path = path
        self.url = url
        self.parent_url = parentUrl
        self.size = size
        self.owner = owner
        self.is_directory = is_directory
        self.is_link = is_link
        self.target_path = target_path
        self.last_modified = last_modified
        self.data_format = data_format
        self.available_data_formats = available_data_formats
        self.effective_acl = effective_acl

    @staticmethod
    def from_json(json_data):
        return GSFileMetadata(
            json_data.get('name'),
            json_data.get('path'),
            json_data.get('url'),
            json_data.get('parentUrl'),
            json_data.get('size'),
            json_data.get('owner'),
            json_data.get('isDirectory'),
            json_data.get('isLink'),
            json_data.get('targetPath'),
            json_data.get('lastModified'),
            GSDataFormat.from_json(json_data.get('dataFormat')),
            [GSDataFormat.from_json(data_fmt)
             for data_fmt in json_data.get('availableDataFormats', [])],
            GSEffectiveAcl.from_json(json_data.get('effectiveAcl'))
        )


class GSDirectoryListing(object):
    """
    See: http://www.genomespace.org/support/api/restful-access-to-dm#appendix_b
    """

    def __init__(self, contents, directory):
        self.contents = contents
        self.directory = directory

    @staticmethod
    def from_json(json_data):
        return GSDirectoryListing(
            [GSFileMetadata.from_json(content)
             for content in json_data.get('contents', [])],
            GSFileMetadata.from_json(json_data.get('directory'))
        )


class GenomeSpaceClient():
    """
    A simple GenomeSpace client
    """

    def __init__(self, username=None, password=None, token=None):
        """
        Constructs a new GenomeSpace client. A username/password
        combination or a token must be supplied.

        :type username: :class:`str`
        :param username: GenomeSpace username

        :type password: :class:`str`
        :param password: GenomeSpace password

        :type token: :class:`str`
        :param token: A GenomeSpace auth token. If supplied, the token will be
                      used instead of the username/password.
        """
        self.username = username
        self.password = password
        self.token = token

    def _get_gs_auth_cookie(self, server_url):
        """
        Returns a cookie containing a GenomeSpace auth token.
        If an auth token was not provided at client initalisation, a request
        is made to the identity server to obtain a new session token.
        """
        if not self.token:
            parsed_uri = urlparse(server_url)
            url = "{uri.scheme}://{uri.netloc}/identityServer/basic".format(
                uri=parsed_uri)
            response = requests.get(url,
                                    auth=requests.auth.HTTPBasicAuth(
                                        self.username,
                                        self.password))
            response.raise_for_status()
            self.token = response.cookies.get("gs-token")
        return {"gs-token": self.token}

    def _api_generic_request(self, request_func, genomespace_url, headers=None,
                             body=None, allow_redirects=True):
        """
        Makes a request to a GenomeSpace API endpoint, after adding some
        standard headers, including authentication headers.
        Also performs some standard validations on the result.

        :type request_func: :func to call. Must be from the requests package,
                            and maybe a get, put, post etc.
        :param request_func: Calls the requested method in the requests package
                            after adding some standard headers.

        :type genomespace_url: :class:`str`
        :param genomespace_url: GenomeSpace API URL to perform the request
                                against.

        :type headers: :class:`dict`
        :param headers: A dict containing additional headers to include with
                        the request.

        :type body: :class:`bytes`
        :param body: Optional data to send as the request body.

        :return: a JSON response after performing some sanity checks. Raises
                 an exception in case of an unexpected response.
        """
        req_headers = {'Accept': 'application/json',
                       'Content-Type': 'application/json'}
        req_headers.update(headers or {})

        response = request_func(genomespace_url,
                                cookies=self._get_gs_auth_cookie(
                                    genomespace_url),
                                headers=req_headers,
                                data=body,
                                allow_redirects=allow_redirects)
        response.raise_for_status()
        return response

    def _api_json_request(self, request_func, genomespace_url, headers=None,
                          body=None):
        """
        Makes a request to a GenomeSpace API endpoint, after adding some
        standard headers, including authentication headers.
        Also performs some standard validations on the result.

        :return: a JSON response after performing some sanity checks. Raises
                 an exception in case of an unexpected response.
        """
        response = self._api_generic_request(request_func,
                                             genomespace_url,
                                             headers=headers,
                                             body=body)
        if "application/json" not in response.headers["content-type"]:
            raise GSClientException("Expected json content but received: %s" %
                                    (response.headers["content-type"],))

        return response.json()

    def _api_get_request(self, genomespace_url, headers=None):
        return self._api_json_request(
            requests.get, genomespace_url, headers=headers)

    def _api_put_request(self, genomespace_url, headers=None, body=None):
        return self._api_json_request(
            requests.put, genomespace_url, headers=headers, body=body)

    def _api_delete_request(self, genomespace_url, headers=None, body=None):
        return self._api_generic_request(
            requests.delete, genomespace_url, headers=headers)

    def _internal_copy(self, source, destination):
        if not gs_glob.is_same_genomespace_server(source, destination):
            raise GSClientException(
                "Copying between two different GenomeSpace servers is"
                " currently unsupported.")
        dest_is_dir = self._is_dir_path(destination)
        for f in gs_glob.gs_iglob(self, source):
            if dest_is_dir:
                basename = os.path.basename(f)
                dstname = destination + "/" + basename
            else:
                dstname = destination
            # GS internal copies automatically handle files or folders
            self._internal_copy_item(f, dstname)

    def _internal_copy_item(self, source, destination):
        copy_source = source.replace(
            gs_glob.GENOMESPACE_URL_REGEX.match(source).group(1),
            "/")
        return self._api_put_request(
            destination, headers={'x-gs-copy-source': copy_source})

    def _get_upload_info(self, genomespace_url):
        url = genomespace_url.replace("/datamanager/v1.0/file/",
                                      "/datamanager/v1.0/uploadinfo/")
        return self._api_get_request(url)

    def _get_download_info(self, genomespace_url):
        response = self._api_generic_request(requests.get, genomespace_url,
                                             allow_redirects=False)
        # This is for an edge case where GenomeSpace urls such as
        # https://dm.genomespace.org/datamanager/file/Home redirect to
        # https://gsui.genomespace.org/datamanager/v1.0/file/Home/ before
        # redirecting to the actual storage URL.
        # Therefore, keep checking the response headers till it
        # no longer matches an API URL.
        redirect_count = 0
        while gs_glob.is_genomespace_url(response.headers['Location']):
            response = self._api_generic_request(requests.get,
                                                 response.headers['Location'],
                                                 allow_redirects=False)
            if redirect_count > 4:
                raise GSClientException("Too many redirects while trying to"
                                        " fetch: {}".format(genomespace_url))
            redirect_count += 1

        return response.headers

    def _upload(self, source, destination, recurse=False):
        dest_is_dir = self._is_dir_path(destination)

        for f in glob.iglob(source):
            if dest_is_dir:
                basename = os.path.basename(f)
                dstname = destination + "/" + basename
            else:
                dstname = destination

            if os.path.isdir(f):
                if dest_is_dir:
                    self._upload_tree(f, dstname, recurse)
                else:
                    raise GSClientException(
                        "Source is a folder, and therefore, the destination"
                        " must also be a folder.")
            else:
                self._upload_file(f, dstname)

    def _upload_tree(self, source, destination, recurse):
        contents = os.listdir(source)
        self.mkdir(destination, create_path=True)
        errors = []
        for item in contents:
            srcname = os.path.join(source, item)
            dstname = destination + "/" + item
            try:
                if os.path.isdir(srcname) and recurse:
                    self._upload_tree(srcname, dstname, recurse)
                else:
                    self._upload_file(srcname, dstname)
            # catch the Error from the recursive upload so that we can
            # continue with other files
            except Exception as err:
                errors.extend(err)
        if errors:
            raise GSClientException("Some errors occurred while uploading:"
                                    " %s" % (errors,))

    def _upload_file(self, source, destination):
        upload_info = self._get_upload_info(destination)
        handler = storage_handlers.create_handler(
            upload_info.get("uploadType"))
        handler.upload(source, upload_info)

    def _download(self, source, destination, recurse=False):
        dest_is_dir = self._is_dir_path(destination)

        for f in gs_glob.gs_iglob(self, source):
            if dest_is_dir:
                basename = os.path.basename(f)
                dstname = destination + "/" + basename
            else:
                dstname = destination

            if self.isdir(f):
                if dest_is_dir:
                    self._download_tree(f, dstname, recurse)
                else:
                    raise GSClientException(
                        "Source is a folder, and therefore, the destination"
                        " must also be a folder.")
            else:
                self._download_file(f, dstname)

    def _download_tree(self, source, destination, recurse):
        contents = self.list(source).contents
        try:
            os.makedirs(destination)
        except OSError as e:
            # be happy if someone already created the path
            if e.errno != errno.EEXIST:
                raise
        errors = []
        for item in contents:
            srcname = source + "/" + item.name
            dstname = os.path.join(destination, item.name)
            try:
                if self.isdir(srcname) and recurse:
                    self._download_tree(srcname, dstname, recurse)
                else:
                    self._download_file(srcname, dstname)
            # catch the Error from the recursive download so that we can
            # continue with other files
            except Exception as err:
                errors.extend(err)
        if errors:
            raise GSClientException("Some errors occurred while downloading:"
                                    " %s" % (errors,))

    def _download_file(self, source, destination):
        download_info = self._get_download_info(source)
        storage_type = gs_glob.GENOMESPACE_URL_REGEX.match(
            source).group(4)
        handler = storage_handlers.create_handler(storage_type)
        handler.download(download_info, destination)

    def _is_dir_path(self, path):
        if gs_glob.is_genomespace_url(path):
            return self.isdir(path)
        else:
            return os.path.isdir(path)

    def copy(self, source, destination, recurse=False):
        """
        Copies a file to/from/within GenomeSpace.

        E.g.
        .. code-block:: python
            client.copy("/tmp/local_file.txt",
                    "https://dm.genomespace.org/datamanager/v1.0/file/Home/MyBucket/hello.txt")

        :type source: :class:`str`
        :param source: Local filename or GenomeSpace URL of source file.

        :type destination: :class:`str`
        :param destination: Local filename or GenomeSpace URL of destination
                            file.

        """
        log.debug("copy: %s -> %s", source, destination)

        if gs_glob.is_genomespace_url(
                source) and gs_glob.is_genomespace_url(destination):
            self._internal_copy(source, destination)
        elif gs_glob.is_genomespace_url(
                source) and not gs_glob.is_genomespace_url(destination):
            self._download(source, destination, recurse=recurse)
        elif not gs_glob.is_genomespace_url(
                source) and gs_glob.is_genomespace_url(destination):
            self._upload(source, destination, recurse=recurse)
        else:
            raise GSClientException(
                "Either source or destination must be a valid GenomeSpace"
                " location")

    def move(self, source, destination):
        """
        Moves a file within GenomeSpace.

        E.g.
        .. code-block:: python
            client.move("https://dm.genomespace.org/datamanager/v1.0/file/Home/MyBucket/hello.txt",
                        "https://dm.genomespace.org/datamanager/v1.0/file/Home/MyBucket/world.txt")

        :type source: :str:
        :param source: GenomeSpace URL of source file. Cannot be a local file.

        :type destination: :str:
        :param destination: Local filename or GenomeSpace URL of destination
                            file. If destination is a local file, the file
                            will be copied to the destination and the source
                            file deleted.
        """
        log.debug("move: %s -> %s", source, destination)
        if gs_glob.is_genomespace_url(source):
            self.copy(source, destination)
            self.delete(source)
        else:
            raise GSClientException(
                "Source must be a valid GenomeSpace location")

    def list(self, genomespace_url):
        """
        Returns a list of files within a GenomeSpace folder.

        E.g.
        .. code-block:: python
            client.list("https://dm.genomespace.org/datamanager/v1.0/file/Home/MyBucket/")

        :type genomespace_url: :class:`str`
        :param genomespace_url: GenomeSpace URL of folder to list.

        :rtype:  :class:`dict`
        :return: a JSON dict in the format documented here:
                 http://www.genomespace.org/support/api/restful-access-to-dm#appendix_b
        """
        log.debug("list: %s", genomespace_url)
        json_data = self._api_get_request(genomespace_url)
        return GSDirectoryListing.from_json(json_data)

    def delete(self, genomespace_url, recurse=False):
        """
        Deletes a file within a GenomeSpace folder.

        E.g.
        .. code-block:: python
            client.delete("https://dm.genomespace.org/datamanager/v1.0/file/Home/MyBucket/world.txt")

        :type genomespace_url: :class:`str`
        :param genomespace_url: GenomeSpace URL of file to delete.
        """
        log.debug("delete: %s", genomespace_url)
        for f in gs_glob.gs_iglob(self, genomespace_url):
            self._delete_item(f, recurse)

    def _delete_item(self, genomespace_url, recurse=False):
        if recurse:
            if self.isdir(genomespace_url):
                for f in self.list(genomespace_url).contents:
                    self._delete_item(f.url, recurse=recurse)

        try:
            self._api_delete_request(genomespace_url)
        except HTTPError as e:
            if e.response.status_code == 404:
                # Folders become non-existent on openstack
                # when the last file gets deleted, so ignore
                pass
            else:
                raise e

    def isdir(self, genomespace_url):
        """
        Returns True if a given genomespace_url is a directory

        :type genomespace_url: :class:`str`
        :param genomespace_url: GenomeSpace URL of file to delete.

        :rtype:  :class:`bool`
        :return: True if the url is a directory. False otherwise.
        """
        try:
            md = self.get_metadata(genomespace_url)
            return md.is_directory
        except GSClientException:
            return False
        except HTTPError as e:
            if e.response.status_code == 404:
                return False
            else:
                raise e

    def mkdir(self, genomespace_url, create_path=True):
        """
        Creates a folder at a given location.

        E.g.
        .. code-block:: python
            client.mkdir("https://dm.genomespace.org/datamanager/v1.0/file/Home/MyBucket/Folder1")

        :type genomespace_url: :class:`str`
        :param genomespace_url: GenomeSpace URL of file to delete.

        :type create_path: :class:`boolean`
        :param create_path: Create intermediate directories as required.
        """
        log.debug("mkdir: %s", genomespace_url)
        if create_path:
            dirname, _ = os.path.split(genomespace_url)
            if not gs_glob.is_genomespace_url(dirname):
                return
            else:
                self.mkdir(dirname, create_path)

        return self._api_put_request(genomespace_url,
                                     body='{"isDirectory": true}')

    def get_metadata(self, genomespace_url):
        """
        Gets metadata information of a genomespace file/folder. See:
        http://www.genomespace.org/support/api/restful-access-to-dm#file_metadata

        E.g.

        .. code-block:: python

            client.get_metadata("https://dm.genomespace.org/datamanager/v1.0/file/Home/MyBucket/world.txt")

        :type genomespace_url: :class:`str`
        :param genomespace_url: GenomeSpace URL of file to delete.

        :rtype:  :class:`dict`
        :return: a JSON dict in the format documented here:
                 http://www.genomespace.org/support/api/restful-access-to-dm#appendix_b
        """
        log.debug("get_metadata: %s", genomespace_url)
        url = re.sub(r"((http[s]?://.*/datamanager/)(v[0-9]+.[0-9]+/)?file)",
                     r'\g<2>v1.0/filemetadata', genomespace_url)
        json_data = self._api_get_request(url)
        return GSFileMetadata.from_json(json_data)

    def get_remaining_token_time(self, genomespace_url):
        """
        Gets the time to live for the gs-token if you have one.
        If you don't have one, will return 0, as the non existent token has
        no time left to live. See:
        http://www.genomespace.org/support/api/restful-access-to-identity-server#get_token_time

        E.g.

        .. code-block:: python

            client.get_remaining_token_time('https://genomespace.genome.edu.au/')

        :type genomespace_url: :class:`str`
        :param genomespace_url: GenomeSpace URL.

        :rtype: :class:`int`
        :return: the time the token has left to live in milliseconds.
        """
        if not self.token:
            return 0
        url_components = urlparse(genomespace_url)
        location = '{uri.scheme}://{uri.netloc}' \
                   '/identityServer/usermanagement/utility/token/remainingTime'
        url = location.format(uri=url_components)
        result = requests.get(url, cookies={"gs-token": self.token})
        if result.status_code == requests.codes.ok:
            return int(result.text)
        return 0
