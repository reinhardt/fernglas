import sys
from ConfigParser import SafeConfigParser
from distutils.core import run_setup
from git import Repo
from os import getcwd
from os import path
from paramiko import AutoAddPolicy
from paramiko.client import SSHClient
from sys import exit

SSH_OPTIONS = ['username', 'password', 'port', 'pkey']


def main():
    user_config_file = path.join(path.expanduser('~'), '.fernglas.cfg')
    project_config_file = path.join(getcwd(), '.fernglas.cfg')
    config = SafeConfigParser()
    config.read([user_config_file, project_config_file])
    servers = {}
    server_sections = config.get('main', 'servers').split(',')
    server_sections = [section.strip() for section in server_sections]
    for server in server_sections:
        servers[server] = dict(config.items(server))
        if 'port' in servers[server]:
            servers[server]['port'] = int(servers[server]['port'])

    issue = sys.argv[1]

    package = run_setup(path.join(getcwd(), 'setup.py'))
    package_name = package.get_name()

    repo = Repo(getcwd())
    latest_issue_commit = repo.git.log(grep=issue, n=1, format='%H')
    if not latest_issue_commit:
        print("No commits found for " + issue)
        exit(1)

    client = SSHClient()
    client.load_system_host_keys()
    # XXX support ecdsa?
    client.set_missing_host_key_policy(AutoAddPolicy())

    for key, server in servers.items():
        connect_opts = dict(
            (opt, servers[key][opt]) for opt in SSH_OPTIONS
            if opt in servers[key])
        client.connect(server['name'], **connect_opts)
        stdin, stdout, stderr = client.exec_command('grep {0} {1}'.format(
            package_name, server['versions-path']))
        deployed_version = stdout.read().strip().replace(package_name, '')\
            .replace('=', '').strip()
        version_tags = [tag for tag in repo.tags
                        if tag.name == deployed_version]
        tag = version_tags[0]
        version_commit = tag.commit.hexsha
        status = repo.is_ancestor(latest_issue_commit, version_commit)
        print("{0} is {2}deployed to {1}".format(
            issue, key, (not status) and 'not ' or ''))
    client.close()
