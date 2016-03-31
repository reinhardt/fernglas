import sys
from ConfigParser import SafeConfigParser
from distutils.core import run_setup
from git import Repo
from os import getcwd
from os import path
from paramiko import AutoAddPolicy
from paramiko.client import SSHClient
from paramiko.config import SSHConfig
from sys import exit

SSH_OPTIONS = ['username', 'password', 'port', 'pkey']
SSH_CONFIG_MAPPING = {
    'user': 'username',
    'identityfile': 'key_filename',
    'hostname': 'hostname',
}


def main():
    user_config_file = path.join(path.expanduser('~'), '.fernglas.cfg')
    project_config_file = path.join(getcwd(), '.fernglas.cfg')
    config = SafeConfigParser()
    config.read([user_config_file, project_config_file])
    servers = {}
    if not config.has_section('main'):
        print("No main config found")
        exit(1)
    if not config.has_option('main', 'servers'):
        print("No servers defined")
        exit(2)
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
    latest_issue_commit = repo.git.log(all=True, grep=issue, n=1, format='%H')
    if not latest_issue_commit:
        print("No commits found for " + issue)
        exit(3)

    config = SSHConfig()
    ssh_config_path = path.expanduser('~/.ssh/config')
    if path.exists(ssh_config_path):
        try:
            config.parse(open(ssh_config_path))
        except Exception as e:
            print("Could not parse ssh config: " + str(e))

    client = SSHClient()
    client.load_system_host_keys()
    # XXX support ecdsa?
    client.set_missing_host_key_policy(AutoAddPolicy())

    for key, server in servers.items():
        host_config = config.lookup(server['hostname'])
        connect_opts = {}
        for key_ssh, key_paramiko in SSH_CONFIG_MAPPING.items():
            if key_ssh in host_config:
                connect_opts[key_paramiko] = host_config[key_ssh]
        connect_opts.update(dict(
            (opt, servers[key][opt]) for opt in SSH_OPTIONS
            if opt in servers[key]))
        client.connect(**connect_opts)
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
