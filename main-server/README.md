# Main Server

This is a web server with endpoints to collect data from other devices on the network.

It will send out alerts via email when trigger conditions are met.
It could possibly send requests back to other devices on the network in the futur.

## SMTP Info

The server needs a json file with smtp info to send emails.
The following example file designates the format:
```
{
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "user_address": "example@gmail.com",
  "user_pass": "super-secure-password"
}
```
