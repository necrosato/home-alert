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
python3 install.py -c /path/to/config/file
```

Python modules needed to create playbook:
* Jinja2
* pyyaml

### Hardware

Has been tested with Logitech USB webcams. Refer to this list and opt for a camera that works fine without a powered usb hub.
https://elinux.org/RPi_USB_Webcams

Has also been tested with raspberry pi cameras.

### Locations

A [home alert node](./home-alert-node/README.md) defines a location. These are logical identifiers for different pieces of the home alert network.
Each location can be alarmed by a set of [triggers](./triggers/README.md).

### Design Diagram

![](https://docs.google.com/drawings/d/e/2PACX-1vSxGCZagLkbymGCKPSnHT8GqstmMvKuXujhe91tW-lp0trkRhOifsZffc3oZiCXkfRLcH44u1iE2d7s/pub?w=1440&h=1080)
