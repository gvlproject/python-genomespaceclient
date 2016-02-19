import re
from urlparse import urlparse

import requests


class GSClientException(Exception):
    pass


class GenomeSpaceClient():
    """
    A Genomespace client
    """
    GENOMESPACE_URL_REGEX = re.compile(
        '(http[s]?://.*/datamanager/v1.0/file/)(\w+)/(\w+)')

    def __init__(self, username=None, password=None, token=None):
        self.username = username
        self.password = password
        self.token = token

    def _get_gs_auth_cookie(self, server_url):
        if self.token:
            return {"gs-token": gsToken}
        parsed_uri = urlparse(server_url)
        host_name = urlparse(server_url).netloc
        data = {
            "openid.ns": "http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0",
            "openid.identity": "http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select",
            "openid.claimed_id": "http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select",
            "openid.mode": "checkid_setup",
            "openid.realm": "{uri.scheme}://{uri.netloc}%2Fjsui%2FopenIdClient%3Fis_return%3Dtrue".format(uri=parsed_uri),
            "openid.return_to": "{uri.scheme}://{uri.netloc}/jsui/openIdClient?is_return=true".format(uri=parsed_uri),
            "user_name": self.username,
            "password": self.password
        }
        url = "{uri.scheme}://{uri.netloc}/identityServer/openIdProvider?_action=authorize".format(
            uri=parsed_uri)
        session = requests.Session()
        session.post(url, data=data)
        return session.cookies

    def _api_generic_request(self, request_func, genomespace_url, headers=None):
        req_headers = {'Content-type': 'application/json'}
        req_headers.update(headers or {})

        response = request_func(genomespace_url,
                                cookies=self._get_gs_auth_cookie(
                                    genomespace_url),
                                headers=req_headers)
        response.raise_for_status()
        if response.headers["content-type"] != "application/json":
            raise GSClientException("Expected json content but received: %s" %
                                    (response.headers["content-type"],))

        return response.json()

    def _api_get_request(self, genomespace_url, headers=None):
        return self._api_generic_request(
            requests.get, genomespace_url, headers=headers)

    def _api_put_request(self, genomespace_url, headers=None):
        return self._api_generic_request(
            requests.put, genomespace_url, headers=headers)

    def _is_genomespace_url(self, url):
        return bool(GenomeSpaceClient.GENOMESPACE_URL_REGEX.match(url))

    def _is_same_genomespace_server(self, url1, url2):
        match1 = GenomeSpaceClient.GENOMESPACE_URL_REGEX.match(url1)
        match2 = GenomeSpaceClient.GENOMESPACE_URL_REGEX.match(url2)
        return match1 and match2 and match1.group(1) == match2.group(1)

    def _internal_copy(self, source, destination):
        if not self._is_same_genomespace_server(source, destination):
            raise GSClientException(
                "Copying between two different GenomeSpace servers is currently unsupported.")

        if source.endswith("/") and not destination.endswith("/"):
            raise GSClientException(
                "Source is a folder, and therefore, the destination must also be a folder.")
        if destination.endswith("/") and not source.endswith("/"):
            # Extract the filename from source and append it to destination
            destination += source.rsplit("/", 1)[-1]

        copy_source = source.replace(
            GenomeSpaceClient.GENOMESPACE_URL_REGEX.match(source).group(1),
            "/")
        return self._api_put_request(
            destination, headers={'x-gs-copy-source': copy_source})

    def copy(self, source, destination):
        if self._is_genomespace_url(
                source) and self._is_genomespace_url(destination):
            self._internal_copy(source, destination)
        elif self.is_genomespace_url(
                source) and not self._is_genomespace_url(destination):
            self._download(source, destination)
        elif not self.is_genomespace_url(
                source) and self._is_genomespace_url(destination):
            self._upload(source, destination)
        else:
            raise GSClientException(
                "Source and destination files are both local. Use your Operating System's copy command.")

    def list(self, genomespace_url):
        return self._api_get_request(genomespace_url)
