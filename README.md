# DockerKnocker
Exploits Aunauth Docker API (Docker Remote API Detection)

First, Find an image

curl http://<target-ip>:xxxx/images/json | jq

Then update the scripts with the proper targeting information


This exfiltrates data out of band to an HTTP exfil server.
