# Ansible Configuration

All of the linux nodes in the home alert system (i.e. control server, home alert nodes, etc), are configured using ansible.

Note that all target hosts must have passwordless sudo set up:
* `$ sudo usermod -aG sudo user`
* Add the line `user ALL=(ALL) NOPASSWD: ALL` to /etc/sudoers

Ensure that Ansible is installed on all target hosts:
* `sudo apt-get install ansible`

To run the playbook over ssh:
```
ansible-playbook playbook.yml -i hosts --key-file $PATH_TO_KEY_FILE
```
or with password login
```
ansible-playbook playbook.yml -i hosts --ask-pass
```
