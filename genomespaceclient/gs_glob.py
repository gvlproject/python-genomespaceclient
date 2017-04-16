# A glob module for genomespace paths
# Used to handle wildcard searches in a manner compatible with
# standard file globbing
import fnmatch
import os
import re
import urlparse


GENOMESPACE_URL_REGEX = re.compile(
    '(http[s]?://.*/datamanager/(v[0-9]+.[0-9]+/)?file/)(\w+)/(\w+)')

# Regex for shell wildcards
MAGIC_CHECK = re.compile('[*?[]')


def is_genomespace_url(url):
    return bool(GENOMESPACE_URL_REGEX.match(url))


def is_same_genomespace_server(url1, url2):
    match1 = GENOMESPACE_URL_REGEX.match(url1)
    match2 = GENOMESPACE_URL_REGEX.match(url2)
    return match1 and match2 and match1.group(1) == match2.group(1)


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

    Matches Python glob module characteristics.
    """
    # Ignore query_str while globbing, but add it back before returning
    query_str = urlparse.urlparse(gs_path).query
    if query_str:
        query_str = "?" + query_str
        gs_path = gs_path.replace(query_str, "")

    dirname, basename = os.path.split(gs_path)
    if not is_genomespace_url(dirname):
        return
    if not has_magic(gs_path):
        yield gs_path + query_str
        return
    if has_magic(dirname):
        dirs = gs_iglob(client, dirname)
    else:
        dirs = [dirname]
    for dirname in dirs:
        for name in glob_in_dir(client, dirname, basename):
            yield dirname + "/" + name + query_str


def glob_in_dir(client, dirname, pattern):
    print("Listing dir %s" % dirname)
    listing = client.list(dirname + "/")
    names = [elem['name'] for elem in listing['contents']]
    return fnmatch.filter(names, pattern)
