tcp_forwarder_ssl
==============

Simple Python script (proxy) to forward TCP traffic through SSL. Requires Python ~3.5

Usage
-----
* `python tcp_forward.py <certificate file> <listen host> <listen port> <remote host> <remote port>`

Examples
--------
* `python tcp_forward.py cert.pem localhost 8080 www.google.com 443`
* `python tcp_forward.py cert.pem localhost 8080 www.google.com 443 debug` to show traffic

Generating self-signed certificate
-------------
In case you want to use a self-signed certificate you can generate it using openssl:
* `openssl req -new -x509 -days 3650 -nodes -out cert.pem -keyout cert.pem -subj /C=US/ST=CA/L=Somewhere/O=Someone/CN=FoobarCA`
