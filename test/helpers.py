import contextlib
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import os
import sys

from genomespaceclient import GenomeSpaceClient
from genomespaceclient import main

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


def get_test_username():
    return os.environ["GENOMESPACE_USERNAME"]


def get_test_password():
    return os.environ["GENOMESPACE_PASSWORD"]


def get_genomespace_client():
    return GenomeSpaceClient(username=get_test_username(),
                             password=get_test_password())


def get_remote_test_folder():
    return os.environ["GENOMESPACE_TEST_FOLDER"]


def get_genomespace_url():
    """
    :return: the scheme and net location of the remote test folder in the form
             of a url. E.g. https://genomespace.genome.edu.au
    :rtype: :class:`str`
    """
    url_components = urlparse(get_remote_test_folder())
    return '{uri.scheme}://{uri.netloc}'.format(uri=url_components)


def run_python_script(command, args):

    @contextlib.contextmanager
    def redirect_argv(new_argv):
        saved_argv = sys.argv[:]
        sys.argv = new_argv
        yield
        sys.argv = saved_argv

    @contextlib.contextmanager
    def redirect_stdout(new_stdout):
        saved_stdout = sys.stdout
        sys.stdout = new_stdout
        yield new_stdout
        sys.stdout = saved_stdout

    with redirect_argv(args):
        with redirect_stdout(StringIO()) as stdout:
            main()
            return stdout.getvalue() or ""
