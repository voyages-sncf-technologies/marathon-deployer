from marathon import MarathonClient, MarathonApp
from marathon.models.deployment import MarathonDeployment
from typing import Union
import time
import sys


# TODO: Timeout mechanism
def wait_for_event(client: MarathonClient, event: str, deployment_id: str):
    for evt in client.event_stream():
        if evt.event_type == event:
            if evt.plan.id == deployment_id:
                return


def wait_for_deployment(client: MarathonClient, deployment: Union[MarathonDeployment, dict]) -> bool:
    def show_affected_apps(target_deploy):
        for aff in target_deploy.affected_apps:
            print('- {}: {}ui/#/apps/{}/debug'.format(aff, srv, aff.replace('/', '%2F')))
    target = None
    if isinstance(deployment, dict):
        if not client.list_deployments():
            print('No deployments in progress. Grace time of 3 seconds.')
            time.sleep(3)
        for current_deployment in client.list_deployments():
            if deployment.get('deploymentId') == current_deployment.id:
                target = current_deployment
    else:
        target = deployment
    if target is None:
        print('Deployment {} not found. Assuming complete.'.format(deployment))
        return False
    if target not in client.list_deployments():
        print('Not found yet. Grace time of 3 seconds.')
        time.sleep(3)
    srv = client.servers if isinstance(client.servers, str) else client.servers[0]
    print('Watching deployment {}'.format(target.id))
    print('Affected apps:')
    show_affected_apps(target)
    try:
        i = 0
        print('Waiting', end='')
        sys.stdout.flush()
        while target in client.list_deployments():
            time.sleep(0.5)
            i += 0.5
            if i % 5 == 0:
                print('.', end='')
                sys.stdout.flush()
        print()
    except KeyboardInterrupt:
        rollback = input('\nRoll back deployment? Type \'YES\' to confirm: ')
        if rollback == 'YES':
            prompt = 'Force it?\n' \
                     'Doing so does not create a new rollback deployment, but forcefully deletes the current one.\n' \
                     'WARNING: APPLICATION MAY BE STUCK IN AN INCONSISTENT STATE.\n' \
                     'NO FURTHER ROLLBACKS WILL BE PERFORMED (even if launched with `--fullrollback`)\n' \
                     'Type \'YES\' to confirm: '
            if input(prompt) == 'YES':
                client.delete_deployment(target.id, force=True)
                print('Deployment deleted. Check status of applications:')
                show_affected_apps(target)
                sys.exit(2)
            deployment = client.delete_deployment(target.id, force=False)
            print('Rollback deployment launched: {}'.format(deployment.get('deploymentId')))
            # Do not wait for this one. It must not be cancelled.
            # TODO: Review options?
            return False

        print('\nDeployment monitoring aborted. Check status in:')
        print('- All deployments: {}/ui/#/deployments'.format(srv))
        show_affected_apps(target)
        sys.exit(1)
    print('Deployment {} complete.'.format(target.id))
    return True


# TODO: Deprecate and migrate to `wait_for_deployment`
def poll_deployments_for_app(client: MarathonClient, app: MarathonApp) -> bool:
    appid = '/' + app.id if not app.id.startswith('/') else app.id
    try:
        while True:
            deployments = client.list_deployments()
            if not deployments:
                print('No deployments active. Assuming complete.')
                return True
            for deploy in deployments:
                if appid not in deploy.affected_apps:
                    print("No deployment involving {}. Assuming complete.".format(appid))
                    return True
            time.sleep(0.1)
    except KeyboardInterrupt:
        if input('Really abort creation?\nType \'YES\' to continue: ') == 'YES':
            print('Aborting. Rollback creation or delete application manually.')
            return False
        return poll_deployments_for_app(client, app)
