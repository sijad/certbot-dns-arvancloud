# ArvanCloud DNS Authenticator certbot plugin

This certbot plugin automates the process of
completing a dns-01 challenge by creating, and
subsequently removing, TXT records using the ArvanCloud DNS API.

## Install

Install this package via pip in the same python environment where you installed your certbot.

```
pip install certbot-dns-arvancloud
```

## Usage

To start using DNS authentication for the ArvanCloud DNS API, pass the following arguments on certbot's command line:

| Option                                                     | Description                                      |
|------------------------------------------------------------|--------------------------------------------------|
| `--authenticator certbot-dns-arvancloud:dns-arvancloud`          | select the authenticator plugin (Required)       |
| `--certbot-dns-arvancloud:dns-arvancloud-credentials`            | ArvanCloud DNS API credentials INI file. (Required) |
| `--certbot-dns-arvancloud:dns-arvancloud-propagation-seconds`    | Seconds to wait for the TXT record to propagate  |

## Credentials


From the ArvanCloud control panel at  go to "API Tokens" and add a personal access token.

An example ``credentials.ini`` file:

```ini
certbot_dns_arvancloud:dns_arvancloud_api_token = Apikey xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxx
```
## Examples
To acquire a certificate for `example.com`
```shell script
certbot certonly \\
 --authenticator certbot-dns-arvancloud:dns-arvancloud \\
 --certbot-dns-arvancloud:dns-arvancloud-credentials /path/to/my/arvancloud.ini \\
 -d example.com
```

To acquire a certificate for ``*.example.com``
```shell script
   certbot certonly \\
     --authenticator certbot-dns-arvancloud:dns-arvancloud \\
     --certbot-dns-arvancloud:dns-arvancloud-credentials /path/to/my/arvancloud.ini \\
     -d '*.example.com'
```

## Thanks to

This package is based on https://github.com/ctrlaltcoop/certbot-dns-hetzner and https://github.com/m42e/certbot-dns-ispconfig

