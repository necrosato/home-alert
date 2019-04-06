import argparse
import yaml
import os
import subprocess

def create_control_server(config_path):
    control_server = {}
    control_server['hosts'] = 'control_server'
    control_server['become'] = True
    control_server['vars_files'] = [ config_path ]
    control_server['roles'] = [ 'control-server' ]


def create_htpasswd(dest, users):
    with open(dest, 'w') as f:
        for creds in users:
            f.write(creds['username'] + ':')
            cmd = ['openssl', 'passwd', '-apr1', creds['password']]
            f.write(subprocess.check_output(cmd).decode('utf-8'))


def main():
    parser = argparse.ArgumentParser(description='Home Alert installation script.')
    parser.add_argument('-c', '--config', type=str, required=True,
                         help='Path to a home alert config file.')
    args = parser.parse_args()

    config = yaml.safe_load(open(args.config, 'r'))
    repo_path = os.path.dirname(os.path.realpath(__file__))

    playbook_path = os.path.join(repo_path, 'ansible/playbook.yml')
    ansible_playbook = []

    # Add control server to playbook
    ansible_playbook.append(create_control_server(os.path.realpath(args.config)))

    # Add control server to inventory
    inventory = '[control_server]\n{} ansible_user={}\n'.format(
            config['control_server']['address'], config['control_server']['user'])

    # Generate .htpasswd file for control server
    htpasswd_path = os.path.join(repo_path, 'ansible/roles/control-server/files/htpasswd')
    create_htpasswd(htpasswd_path, config['control_server']['web_credentials'])

    for main_server in config['main_servers']:
        # Build main server config file
        main_server_config_path = os.path.join(repo_path, 'ansible/vars/' + main_server['location'] + '.yml')
        main_server_config = {}
        main_server_config['notify_emails'] = config['notify_emails']
        main_server_config['smtp_info'] = config['smtp_info']
        main_server_config['main_server'] = main_server
        yaml.dump(main_server_config, open(main_server_config_path, 'w'), default_flow_style=False)

        # Add main server play to playbook
        host = {}
        host['hosts'] = main_server['location']
        host['become'] = True
        host['vars_files'] = [ main_server_config_path ]
        host['roles'] = [ 'main-server' ]
        ansible_playbook.append(host)
        # Add main server to inventory
        inventory += '[{}]\n{} ansible_user={}\n'.format(
                main_server['location'], main_server['address'], main_server['user'])

    yaml.dump(ansible_playbook, open(playbook_path, 'w'), default_flow_style=False)
    inventory_path = os.path.join(repo_path, 'ansible/hosts')
    with open(inventory_path, 'w') as f:
        f.write(inventory)

    
if __name__ == '__main__':
    main()
