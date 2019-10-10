import argparse
import sys

from marathon import MarathonClient
from marathon.exceptions import MarathonError


def parse_arguments():
    args = argparse.ArgumentParser()
    args.add_argument('--marathon', '-m', default='http://localhost:8080', help='Marathon where to run the application.'
                                                                                'Allows several URLs, comma separated.')
    args.add_argument('--user', '-u', default='',
                      help='User Marathon where to run the application.')
    args.add_argument('--password', '-p', default='',
                      help='Password Marathon where to run the application.')
    args.add_argument('--appid', type=str,
                      help='App ID of the affected app (e.g.: "/db/mysql")')
    args.add_argument('--put', type=str, help='Path to the JSON definition of the app to be created (or updated if'
                                              'it exists), or path to the folder with JSONs to be created/updated.')
    args.add_argument('--fullrollback', action='store_true', help='In case of deployment cancellation, '
                                                                  'rollback all apps. (Default: disabled)'
                                                                  '\nSee README.md for more info.')
    args.add_argument('--tag', type=str,
                      help='Docker tag to update the app to; it only updates the tag (Requires --appid)')
    args.add_argument('--restart', action='store_true',
                      help='Rolling-restart the app (Requires --appid)')
    args.add_argument('--inplacerestart', action='store_true', help='Restart the app in-place'
                                                                    '(Requires --appid, **implies downtime**)')
    args.add_argument('--scale', type=int,
                      help='Re-scale an application (Requires --appid)')
    args.add_argument('--instances', action='store_true',
                      help='Get the number of instances of an app (Requires --appid)')
    args.add_argument('--list', action='store_true',
                      help='List all apps and their image tags')
    args.add_argument('--saveapp', type=str,
                      help='Save an app\'s JSON definition')
    args.add_argument('--dumpall', action='store_true', help='Save all applications JSONs to a folder '
                                                             '(default: ./backup_<date>')
    args.add_argument('--https-verify', action='store_true', help='Enable HTTPS certificates check')
    args.add_argument('--version', '-v', help='Show version and exit', action="store_true")

    return args.parse_args()


def create_client(urls: str, user: str, password: str, https_verify: bool):
    marathonlist = urls.split(',')
    client = MarathonClient(marathonlist,
                            username=user,
                            password=password,
                            verify=https_verify,
                            timeout=10)  # in seconds
    try:
        ping_answer = client.ping().strip().decode()
        print(ping_answer)
        if ping_answer != '"pong"':
            raise MarathonError
    except MarathonError:
        print('Could not connect to Marathon in {}'.format(marathonlist))
        sys.exit(1)
    return client


def check_appid(appid) -> bool:
    if appid is None:
        print("Error! --appid is required for the requested operation.")
        sys.exit(1)
    else:
        return True
