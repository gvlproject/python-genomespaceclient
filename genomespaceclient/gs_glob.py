# A glob module for genomespace paths
# Used to handle wildcard searches in a manner compatible with
# standard file globbing
import fnmatch
import os
import re
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


GENOMESPACE_URL_REGEX = re.compile(
    '(http[s]?://.*/datamanager/(v[0-9]+.[0-9]+/)?file/)(\w+)/(\w+)')

# Regex for shell wildcards. Identical to standard globs except for '?' which
# cannot be used in a url since it denotes the start of a query string
MAGIC_CHECK = re.compile('[*[]')


def is_genomespace_url(url):
    return bool(GENOMESPACE_URL_REGEX.match(url))


def is_same_genomespace_server(url1, url2):
    match1 = GENOMESPACE_URL_REGEX.match(url1)
    match2 = GENOMESPACE_URL_REGEX.match(url2)
    return match1 and match2 and match1.group(1) == match2.group(1)


def gs_path_split(genomespace_url):
    query_str = urlparse(genomespace_url).query
    if query_str:
        query_str = "?" + query_str
        genomespace_url = genomespace_url.replace(query_str, "")

    dirname, basename = os.path.split(genomespace_url)
    return dirname, basename, query_str


def has_magic(s):
    """
    Checks whether a given string contains shell wildcard characters
    """
    return MAGIC_CHECK.search(s) is not None


def find_magic_match(s):
    """
    Returns the position of a wildcard
    """
    return MAGIC_CHECK.search(s)


def gs_iglob(client, gs_path):
    """
    Returns an iterator which yields genomespace paths matching a given
    pattern.
    E.g.
    https://dm.genomespace.org/datamanager/v1.0/file/Home/folder1/*.txt

    would return all files in folder1 with a txt extension such as:
    https://dm.genomespace.org/datamanager/v1.0/file/Home/folder1/a.txt
    https://dm.genomespace.org/datamanager/v1.0/file/Home/folder1/b.txt

    Matches Python glob module characteristics except for '?' which is
    unsupported.
    """
    # Ignore query_str while globbing, but add it back before returning
    dirname, basename, query_str = gs_path_split(gs_path)
    if not is_genomespace_url(dirname):
        return
    if not has_magic(gs_path):
        if basename:
            yield gs_path
        else:
            # Patterns ending with a slash should match only directories
            if client.isdir(dirname):
                yield gs_path
        return
    if has_magic(dirname):
        dirs = gs_iglob(client, dirname)
    else:
        dirs = [dirname]

    if has_magic(basename):
        glob_in_dir = _glob1
    else:
        glob_in_dir = _glob0
    for dirname in dirs:
        for name in glob_in_dir(client, dirname, basename):
            yield dirname + "/" + name + query_str


# See python glob module implementation, which this is closely based on
def _glob1(client, dirname, pattern):
    if client.isdir(dirname):
        listing = client.list(dirname + "/")
        names = [entry.name for entry in listing.contents]
        return fnmatch.filter(names, pattern)
    else:
        return []


def _glob0(client, dirname, basename):
    if basename == '':
        # `os.path.split()` returns an empty basename for paths ending with a
        # directory separator.  'q*x/' should match only directories.
        if client.isdir(dirname):
            return [basename]
    else:
        return [basename]
    return []
