#!/usr/bin/env python3

from marathon_deploy.utils.common import parse_arguments, create_client
import os
import sys
import time

# Hide urllib warnings for insecure certificates
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import warnings
warnings.filterwarnings("ignore", category=InsecureRequestWarning)


def main():
    args = parse_arguments()

    if args.appid is None:
        print("appid must be defined ")
        sys.exit(1)

    client = create_client(args.marathon, args.user, args.password, args.https_verify)

    time.sleep(int(os.environ.get('INITIAL_SLEEP_DURATION', '20')))

    while True:
        my_app = client.get_app(args.appid)
        constraint = my_app.constraints and my_app.constraints[0]
        print(constraint, 'tasks_running:', my_app.tasks_running)
        if my_app.tasks_running >= 1 and my_app.tasks_healthy >= 1:
            print("APP deploy on Marathon ")
            break
        if my_app.tasks_staged >= 1:
            print("APP in staging mode ")

        time.sleep(1)


if __name__ == '__main__':
    main()
