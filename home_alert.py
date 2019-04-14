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


def create_trigger_esp8266(main_server, control_server, wifi):
    '''
    Generate the files needed for an esp8266 trigger
    '''
    location = main_server['location']
    print('Creating {} esp8266 trigger'.format(location))
    trigger = main_server['triggers']['esp8266']

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

def create_triggers(main_server, control_server, wifi):
    '''
    Dispatch a trigger create method given a type
    '''
    if 'triggers' in main_server:
        for trigger_type in main_server['triggers']:
            if trigger_type in TRIGGER_TYPES:
                # Call to create method
                TRIGGER_TYPES[trigger_type](main_server, control_server, wifi)


def main():
    parser = argparse.ArgumentParser(description='Home Alert installation script.')
    parser.add_argument('-c', '--config', type=str, required=True,
                         help='Path to a home alert config file.')
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

    for main_server in config['main_servers']:
        # Generate trigger resources
        create_triggers(main_server, config['control_server'], config['wifi'])

        # Build main server config file
        main_server_config = {}
        main_server_config['notify_emails'] = config['notify_emails']
        main_server_config['smtp_info'] = config['smtp_info']
        main_server_config['main_server'] = main_server
        main_server_config_path = os.path.join(REPO_PATH, 'ansible/vars/' + main_server['location'] + '.yml')
        if 'aws' in config:
            main_server_config['s3_upload_bucket'] = config['aws']['s3_upload_bucket']
        yaml.dump(main_server_config, open(main_server_config_path, 'w'), default_flow_style=False)

        # Add main server play to playbook
        host = {}
        host['hosts'] = main_server['location']
        host['become'] = True
        host['vars_files'] = [ main_server_config_path ]
        host['roles'] = [ 'main-server' ]
        if 'aws' in config:
            host['vars_files'].append(aws_config_path)
            host['roles'].append('aws')
        host['vars'] = { 'user': 'main-server' }
        ansible_playbook.append(host)
        # Add main server to inventory
        inventory += '[{}]\n{} ansible_user={}\n'.format(
                main_server['location'], main_server['address'], main_server['user'])

    # Generate .htpasswd file for control server
    htpasswd_path = os.path.join(REPO_PATH, 'ansible/roles/control-server/files/htpasswd')
    create_htpasswd(htpasswd_path, config['control_server']['web_credentials'])

    # Write playbook
    yaml.dump(ansible_playbook, open(playbook_path, 'w'), default_flow_style=False)
    # Write inventory file
    inventory_path = os.path.join(REPO_PATH, 'ansible/hosts')
    with open(inventory_path, 'w') as f:
        f.write(inventory)

    
if __name__ == '__main__':
    main()
