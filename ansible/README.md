# Ansible Configuration

All of the linux nodes in the home alert system (i.e. control server, home alert nodes, etc), are configured using ansible.

Note that all target hosts must have passwordless sudo set up:
* `$ sudo usermod -aG sudo user`
* Add the line `user ALL=(ALL) NOPASSWD: ALL` to /etc/sudoers

Ensure that Ansible is installed on all target hosts:
* `sudo apt-get install ansible`
