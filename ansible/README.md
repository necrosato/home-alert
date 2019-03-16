# Ansible Configuration

All of the linux nodes in the home alert system (i.e. main server, streaming server, etc), are configured using ansible.

Note that all target hosts must have passworldless sudo set up:
```
sudo usermod -aG sudo user
user ALL=(ALL) NOPASSWD: ALL
```

First on the target hosts:
```
sudo apt-get intall ansible
```

To run the playbook over ssh:
```
ansible-playbook playbook.yml -i hosts --key-file $PATH_TO_KEY_FILE
```
or with password login
```
ansible-playbook playbook.yml -i hosts --ask-pass
```
