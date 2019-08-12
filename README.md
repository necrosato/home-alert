# Home Alert

An open source security system powered by a low cost distributed iot system.

## Prerequisites

Some steps must be taken on each host that is going to have home alert software installed on it.
1. Setup passwordless sudo for a user:
 * `$ sudo usermod -aG sudo user`
 * Add the line `user ALL=(ALL) NOPASSWD: ALL` to /etc/sudoers
2. Ensure that the host used to deploy the installation can ssh into each of the users of the target hosts via ssh keys.
3. Install ansible
 * `$ sudo apt-get install ansible`

## Installation

To install the home alert security system software on your own hosts, first copy and modify the [example configuration yaml file](./config_example.yaml).
```
git clone https://github.com/necrosato/home-alert /tmp/home-alert
cd /tmp/home-alert
# Copy and modify config file ...
python3 home-alert.py -c /path/to/config/file
ansible-playbook -i ./ansible/hosts ./ansible/playbook.yml
```

### Hardware

Has been tested with Logitech USB webcams. Refer to this list and opt for a camera that works fine without a powered usb hub.
https://elinux.org/RPi_USB_Webcams

Has also been tested with raspberry pi cameras.

### Locations

A [main server](./main-server/README.md) defines a location. These are logical identifiers for different pieces of the home alert network.
Each location can be alarmed by a set of [triggers](./trigger/README.md).

### Design Diagram

![](https://docs.google.com/drawings/d/e/2PACX-1vSEVFTtqQK6O_ZhOK2cQsX6Z9cOhI2-P0edLwlsttmLBTdILeRkZJulocc0ExMeHQ3qqyrDxjxTxg7x/pub?w=1440&h=1080)
