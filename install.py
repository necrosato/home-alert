import argparse
import yaml
import os
import shutil
import subprocess
import random
import string
import jinja2

# Constants

REPO_PATH = os.path.dirname(os.path.realpath(__file__))

def create_control_server(config_path):
    '''
    Create control play for ansible playbook
    '''
    control_server = {}
    control_server['hosts'] = 'control_server'
    control_server['become'] = True
    control_server['vars_files'] = [ config_path ]
    control_server['roles'] = [ 'control-server' ]
    control_server['vars'] = { 'user': 'control-server' }
    return control_server


def create_htpasswd(dest, users):
    '''
    Create htpasswd file from list of usernames and passwords
    '''
    with open(dest, 'w') as f:
        for creds in users:
            f.write(creds['username'] + ':')
            cmd = ['openssl', 'passwd', '-apr1', creds['password']]
            f.write(subprocess.check_output(cmd).decode('utf-8'))


def random_generator(size=8, chars=string.ascii_letters + string.digits):
    '''
    A random string generator
    '''
    return ''.join(random.choice(chars) for x in range(size))


def create_trigger_esp8266(home_alert_node, control_server, wifi):
    '''
    Generate the files needed for an esp8266 trigger
    '''
    location = home_alert_node['location']
    print('Creating {} esp8266 trigger'.format(location))
    trigger = home_alert_node['triggers']['esp8266']

    # Generate credentials using location as username and random password
    username = location + '_trigger_' + random_generator(4, string.digits)
    password = random_generator(32)
    trigger_creds = { 'username': username, 'password': password }
    trigger['web_credentials'] = trigger_creds
    control_server['web_credentials'].append(trigger_creds)

    example_dir = REPO_PATH + '/triggers/esp8266_example/trigger'
    # Render jinja2 arduino config template
    with open(example_dir + '/config.h.j2', 'r') as f:
        config_template = jinja2.Template(f.read())
    trigger_config = config_template.render(location=location,
            control_server_address=control_server['address'], wifi=wifi, trigger=trigger)
    
    # Copy sketch files
    trigger_dir = REPO_PATH + '/triggers/build/' + location + '/esp8266'
    if not os.path.exists(trigger_dir):
        os.makedirs(trigger_dir)
    trigger_sketch_dir = trigger_dir + '/trigger'
    # Dest dir must not exist for copytree to work
    if os.path.exists(trigger_sketch_dir):
        shutil.rmtree(trigger_sketch_dir)
    shutil.copytree(example_dir, trigger_sketch_dir, ignore=shutil.ignore_patterns('*.j2'))
    with open(trigger_sketch_dir + '/config.h', 'w') as f:
        f.write(trigger_config + '\n')


# Dispatch dictionary to create different trigger types
TRIGGER_TYPES = {'esp8266': create_trigger_esp8266 }

def create_triggers(home_alert_node, control_server, wifi):
    '''
    Dispatch a trigger create method given a type
    '''
    if 'triggers' in home_alert_node:
        for trigger_type in home_alert_node['triggers']:
            if trigger_type in TRIGGER_TYPES:
                # Call to create method
                TRIGGER_TYPES[trigger_type](home_alert_node, control_server, wifi)


def run_ansible_playbook(inventory, playbook, args):
    ''' Run ansible-playbook given paths to an inventory file and playbook '''
    ansible_cmd = ['ansible-playbook', '-i', inventory, playbook]
    if args.dry_run:
        ansible_cmd.append('--check')
    if args.ask_sudo_pass:
        ansible_cmd.append('--ask-become-pass')
    subprocess.check_call(ansible_cmd)


def main():
    parser = argparse.ArgumentParser(description='Home Alert installation script.')
    parser.add_argument('-c', '--config', type=str, required=True,
                        help='Path to a home alert config file.')
    parser.add_argument('-d', '--dry_run', default=False, action='store_true',
                        help='Do not actually install on target hosts, '
                             'Generates all resources needed to run the '
                             'ansible playbook for installation.')
    parser.add_argument('--ask_sudo_pass', default=False, action='store_true',
                        help='Ask for the sudo password on remote machines. '
                             'Used if an installation target host cannot '
                             'execute passwordless sudo as the user provided.')
    args = parser.parse_args()

    config = yaml.safe_load(open(args.config, 'r'))

    playbook_path = os.path.join(REPO_PATH, 'ansible/playbook.yml')
    ansible_playbook = []

    # Add control server to playbook
    ansible_playbook.append(create_control_server(os.path.realpath(args.config)))

    # Add control server to inventory
    inventory = '[control_server]\n{} ansible_user={}\n'.format(
            config['control_server']['address'], config['control_server']['user'])

    # Generate aws yaml file if defined
    aws_config_path = os.path.join(REPO_PATH, 'ansible/vars/aws.yml')
    if 'aws' in config:
        yaml.dump(config['aws'], open(aws_config_path, 'w'), default_flow_style=False)

    for home_alert_node in config['home_alert_nodes']:
        # Generate trigger resources
        create_triggers(home_alert_node, config['control_server'], config['wifi'])

        # Build node config file
        home_alert_node_config = {}
        home_alert_node_config['notify_emails'] = config['notify_emails']
        home_alert_node_config['smtp_info'] = config['smtp_info']
        home_alert_node_config['home_alert_node'] = home_alert_node
        home_alert_node_config_path = os.path.join(REPO_PATH, 'ansible/vars/' + home_alert_node['location'] + '.yml')
        if 'aws' in config:
            home_alert_node_config['s3_upload_bucket'] = config['aws']['s3_upload_bucket']
        yaml.dump(home_alert_node_config, open(home_alert_node_config_path, 'w'), default_flow_style=False)

        # Add home alert node play to playbook
        host = {}
        host['hosts'] = home_alert_node['location']
        host['become'] = True
        host['vars_files'] = [ home_alert_node_config_path ]
        host['roles'] = [ 'home-alert-node' ]
        if 'aws' in config:
            host['vars_files'].append(aws_config_path)
            host['roles'].append('aws')
        # Check camera type
        if home_alert_node['cam_type'] == "pi":
            host['roles'].append('pi-camera')
        host['vars'] = { 'user': 'home-alert' }
        ansible_playbook.append(host)
        # Add home alert node to inventory
        inventory += '[{}]\n{} ansible_user={}\n'.format(
                home_alert_node['location'], home_alert_node['address'], home_alert_node['user'])

    # Generate .htpasswd file for control server
    htpasswd_path = os.path.join(REPO_PATH, 'ansible/roles/control-server/files/htpasswd')
    create_htpasswd(htpasswd_path, config['control_server']['web_credentials'])

    # Write playbook
    yaml.dump(ansible_playbook, open(playbook_path, 'w'), default_flow_style=False)
    # Write inventory file
    inventory_path = os.path.join(REPO_PATH, 'ansible/hosts')
    with open(inventory_path, 'w') as f:
        f.write(inventory)
    # Run ansible playbook
    run_ansible_playbook(inventory_path, playbook_path, args)

    
if __name__ == '__main__':
    main()
