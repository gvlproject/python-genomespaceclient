import argparse
from datetime import datetime
import json

from client import GenomeSpaceClient
import util


def get_client(args):
    return GenomeSpaceClient(args.user, args.password,
                             args.token)


def genomespace_copy_files(args):
    client = get_client(args)
    client.copy(args.source, args.destination)


def genomespace_delete_files(args):
    client = get_client(args)
    client.delete(args.file_url)


def genomespace_list_files(args):
    client = get_client(args)
    dir_contents = client.list(args.folder_url)

    for dir in dir_contents["contents"]:
        print("{isdir:<3s} {owner:<10s} {size:>10s} {last_modified:>26s} {name:s}".format(
            isdir="d" if dir["isDirectory"] else "_",
            owner=dir["owner"]["name"],
            size=util.format_file_size(dir["size"]),
            last_modified=dir.get("lastModified", ""),
            name=dir.get("name")))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    grp_auth_userpass = parser.add_argument_group(
        'user_pass_auth', 'username/password based authentication')
    grp_auth_userpass.add_argument('-u', '--user', type=str,
                                   help="GenomeSpace username", required=False)
    grp_auth_userpass.add_argument('-p', '--password', type=str,
                                   help="GenomeSpace password", required=False)
    grp_auth_token = parser.add_argument_group(
        'token_auth',
        'token based authentication  (instead of username/password)')
    grp_auth_token.add_argument(
        '-t', '--token', type=str,
        help="GenomeSpace auth token",
        required=False)
    subparsers = parser.add_subparsers(metavar='<subcommand>')

    # upload commands
    file_copy_parser = subparsers.add_parser(
        'cp',
        formatter_class=argparse.RawTextHelpFormatter,
        help='Copy a file from/to/within GenomeSpace',
        description='''
Examples:

1. Copy a local file to GenomeSpace dir
{0} cp /tmp/myfile.txt https://dmdev.genomespace.org/datamanager/v1.0/file/Home/s3:test/

2. Copy a remote file from GenomeSpace to a local file
{0} cp https://dmdev.genomespace.org/datamanager/v1.0/file/Home/s3:test/hello.txt /tmp/myfile.txt

3. Copy a file within GenomeSpace
{0} cp https://dmdev.genomespace.org/datamanager/v1.0/file/Home/s3:test/hello.txt https://dmdev.genomespace.org/datamanager/v1.0/file/Home/s3:test/hello2.txt

'''.format(parser.prog))
    file_copy_parser.add_argument('source', type=str,
                                  help="Local path or GenomeSpace URI of source file")
    file_copy_parser.add_argument('destination', type=str,
                                  help="Local path or GenomeSpace URI of destination file")
    file_copy_parser.set_defaults(func=genomespace_copy_files)

    # download commands
    gs_list_parser = subparsers.add_parser(
        'ls',
        help='List contents of a GenomeSpace folder')
    gs_list_parser.add_argument('folder_url', type=str,
                                help="GenomeSpace URI of folder to list")
    gs_list_parser.set_defaults(func=genomespace_list_files)

    # delete commands
    gs_list_parser = subparsers.add_parser(
        'rm',
        help='Delete a GenomeSpace file or folder')
    gs_list_parser.add_argument('file_url', type=str,
                                help="GenomeSpace URI of file/folder to delete")
    gs_list_parser.set_defaults(func=genomespace_delete_files)

    args = parser.parse_args()
    args.func(args)
