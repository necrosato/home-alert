# Control Server

This is the main user interacting component. It's main job is to function as a reverse proxy, forwarding requests to the proper main server. The control server authenticates public connections and encrypts with ssl.

## Components

### Reverse Proxy

A reverse proxy server is needed to redirect traffic from the user facing control server to the protected main server.
This is needed for three reasons, one being a single point of authentication. The second reason is it will make it possible to use the system from outside the local network. Finally, it will be much easier to just set up ssl on one box than every box running a web server.

### Authentication

Users should not be able to access the main servers directly. For security reasons, the only things that can talk to a main server are a trigger or the control server. Authentication into the control server will be needed as it may be public facing, or maybe you just have mean house mates.

### DNS Server

This should be able to resolve names like home-alert.location to main server ip addresses within the internal network.

### Dynamic DNS

Should update public IP settings so system is always publicly available
