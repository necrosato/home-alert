import argparse
import yaml
import os

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
    control_server = {}
    control_server['hosts'] = 'control_server'
    control_server['become'] = True
    control_server['vars_files'] = [ os.path.realpath(args.config) ]
    control_server['roles'] = [ 'control-server' ]
    ansible_playbook.append(control_server)

    inventory = '[control_server]\n{} ansible_user={}\n'.format(
            config['control_server']['address'], config['control_server']['user'])


    for main_server in config['main_servers']:
        # Build main server config file
        main_server_config_path = os.path.join(repo_path, 'ansible/vars/' + main_server['location'] + '.yml')
        main_server_config = {}
        main_server_config['notify_emails'] = config['notify_emails']
        main_server_config['smtp_info'] = config['smtp_info']
        main_server_config['location'] = main_server['location']
        main_server_config['address'] = main_server['address']
        main_server_config['server_port'] = main_server['server_port']
        main_server_config['upload_path'] = main_server['upload_path']
        main_server_config['video_device'] = main_server['video_device']
        main_server_config['video_width'] = main_server['video_width']
        main_server_config['video_height'] = main_server['video_height']
        main_server_config['opencv_install'] = main_server['opencv_install']
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
