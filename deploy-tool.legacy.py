#!/usr/bin/env python3

import requests
import argparse
import urllib
import json
import time
import os

actions = ('restart', 'put', 'inplacerestart', 'scale', 'instances')

args = argparse.ArgumentParser()
args.add_argument('--marathon', '-m', required=True, help='Marathon where to run the application')
args.add_argument('--appid', type=str, help='App ID of the affected app (e.g.: "/db/mysql")')
#args.add_argument('--action', type=str help='See readme.md!')
#args.add_argument('--create', type=str, help='Path to the JSON definition of the app to be created')
args.add_argument('--put', type=str, help='Path to the JSON definition of the app to be created (or updated if it exists)')
args.add_argument('--tag', type=str, help='Docker tag to update the app to; it only updates the tag (Requires --appid)')
args.add_argument('--restart', action='store_true', help='Rolling-restart the app (Requires --appid)')
args.add_argument('--inplacerestart', action='store_true', help='Restart the app in-place (Requires --appid, **implies downtime**)')
args.add_argument('--scale', type=int, help='Re-scale an application (Requires --appid)')
args.add_argument('--instances', action='store_true', help='Get the number of instances of an app (Requires --appid)')
args.add_argument('--async', action='store_true', help='Do not wait for the deployment to complete (true/false; default: false)')
## ---
# args.add_argument('--definition', type=str, help='Path to the JSON file where the app is defined')
# args.add_argument('--scale', type=int, help='Re-scale an application')

args = args.parse_args()


def main():
    if args.put is not None:
        # TODO: Test sync/monitoring
        put_app(args.marathon, args.put)

    elif args.tag is not None and check_appid():
        update_app_tag(args.marathon, args.appid, args.tag)

    elif args.restart and check_appid():
        rolling_restart_app(args.marathon, args.appid)

    elif args.inplacerestart and check_appid():
        in_place_restart(args.marathon, args.appid)

    elif args.scale is not None and check_appid():
        scale_application(args.marathon, args.appid, args.scale)

    elif args.instances and check_appid():
        print(get_instances_amount(args.marathon, args.appid))

    else:
        print("How the hell did you get here?")
        exit(0)

    if not args.async:
        wait_for_deployment(args.marathon, args.appid)


def check_appid() -> bool:
    if args.appid is None:
        print("Error! --appid is required for the requested operation.")
        exit(1)
    else:
        return True


def get_apps_api(marathon):
    marathon = marathon if marathon.endswith('/') else marathon + '/'
    return marathon + "v2/apps"


def get_deployments_api(marathon):
    marathon = marathon if marathon.endswith('/') else marathon + '/'
    return marathon + "v2/deployments"


def in_place_restart(marathon, appid):
    u = get_apps_api(marathon) + appid
    i = requests.get(u).json().get('app').get('instances')
    scale_application(marathon, appid, 0)
    scale_application(marathon, appid, i)


def scale_application(marathon, appid, instances):
    u = get_apps_api(marathon) + appid
    if get_instances_amount(marathon, appid) == instances:
        print('App {} already has {} instances'.format(appid, instances))
        return
    requests.put(u, json.dumps({'instances': instances}))
    print("Waiting...")
    time.sleep(5)
    a = get_instances_amount(marathon, appid)
    while a is not None and a != instances:
        print("Still scaling. Instances: {} of {}".format(a, instances))
        time.sleep(5)
        a = get_instances_amount(marathon, appid)
    print("Scaling complete. {app} has {n} instances".format(app=appid, n=instances))


def rolling_restart_app(marathon, appid):
    u = get_apps_api(marathon) + appid + "/restart"
    return requests.post(u).status_code == 200


def put_app(marathon, appdefinition):
    if not os.path.isdir('./backups'):
        os.mkdir('./backups/')
        print('Created backups directory')
    with open(appdefinition) as f:
        j = json.load(f)
    if type(j) == dict:
        # if it's a single app, wrap it into a list,
        # so it's compatible with PUT
        j = [j]
    for each in j:
        r = requests.get(get_apps_api(marathon) + '/' + each.get('id'))
        if r.status_code == 404:
            print('App {} does not exist yet. Not backing up.'.format(each.get('id')))
        else:
            existing = r.json().get('app')
            # print(existing)
            if 'fetch' in existing.keys() and 'uris' in existing.keys():
                # Having both keys is invalid, however
                # the /apps endpoint responds this way...
                existing.pop('fetch')
            existing.pop('version')
            bkup = './backups/{}.{}.json'.format(existing.get('id').split('/')[-1], time.strftime("%Y-%m-%d_%H:%M:%S"))
            with open(bkup, 'w') as f:
                f.write(json.dumps(existing, indent=2))
            print('Backed app in {}'.format(bkup))
    # PUT to create or update, as needed (instead of post)
    r = requests.put(get_apps_api(marathon), json=j)
    # r = requests.post(get_apps_api(marathon), s)
    print(r.text)


def destroy_app(marathon, appid):
    u = get_apps_api(marathon) + appid
    print('Destroying app: {}'.format(appid))
    requests.delete(u)
    while requests.get(u).status_code != 404:
        print("Waiting for app to be gone")
        time.sleep(1)


def wait_for_deployment(marathon, appid):
    # TODO: Use streaming API
    def get_deployments():
        return requests.get(get_deployments_api(marathon)).json()

    if len(get_deployments()) == 0:
        return
    while any(list(map(lambda x: appid in x.get('affectedApps'), get_deployments()))):
        print('App {} is being deployed. Hold up...'.format(appid))
        time.sleep(5)
    return


def get_instances_amount(marathon, appid):
    a = requests.get(get_apps_api(marathon) + appid).json().get('app').get('instances')
    return a if type(a) is int else 0


def get_app_defininition(marathon, appid):
    u = get_apps_api(marathon) + appid
    return requests.get(u).json()


def update_app_tag(marathon, appid, tag):
    u = get_apps_api(marathon) + appid
    c = get_app_defininition(marathon, appid).get('app').get('container')
    old_image = c.get('docker').get('image')
    old_tag = old_image.split(':')[-1]
    new_image = old_image.replace(old_tag, tag)
    definition = {
        "container": {
            "volumes": c.get('volumes'),
            "docker": {
                "image": new_image,
                "network": c.get('docker').get('network'),
                "portMappings": c.get('docker').get('portMappings'),
                "privileged": c.get('docker').get('privileged'),
                "parameters": c.get('docker').get('parameters'),
                "forcePullImage": c.get('docker').get('forcePullImage')
            }
        }
    }
    r = requests.put(u, json.dumps(definition))
    print(r.text)


if __name__ == '__main__':
    #if args.action not in actions:
    #    print("Invalid action. Possible actions are:")
    #    print(", ".join(actions))
    #    exit(1)
    #if args.action == 'update' and args.tag is None:
    #    print("Docker Tag (--tag) is required for update action")
    #    exit(1)
    if args.appid is not None:
        args.appid = args.appid if args.appid.startswith('/') else '/' + args.appid
    main()
