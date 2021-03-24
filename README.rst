SocketSrv
=========

One-file python server for low level protocols.

This server listens for incoming messages from multiple protocols and dumps data as it comes. It also allows to send back messages to connected clients.

It is aimed at helping when integrating a low level protocol to an application by being a ready to use server to test your client against.

Usage:
------

In a terminal, start SocketSrv::

	python socketsrv.py

In another terminal, start a client::

	nc localhost 1234

You should see a message from SocketSrv stating that a new TCP connection was made.

To send messages from nc to SocketSrv, just type it in nc's standard input.

To send messages from SocketSrv to nc, use the "send" command in SocketSrv::

	send tcp 0 hello dear tcp client

Commands list
-------------

``help``
	Shows a little help message, protocols list and commands list

``list_clients``
	Shows a list of all connected clients by protocol

``send``
	Send a text message to a connected client (see ``send help`` for more details)

``sendb``
	Send a binary message to a connected client (see ``send help`` for more details)

Protocols list
--------------

 - TCP
 - UDP
 - WebSocket

Advantages over netcat
----------------------

Netcat is a standard tool that works very well for testing TCP and UDP connections.

SocketSrv is a more specialized tool and features some ease of use in the case of testing low-level client developments:

 - Allows multiple connections per instance,
 - provides support for WebSockets,
 - shows more complete information about connections/disconnections of clients,
 - has an extensible interractive commands system,
 - I coded it myself, so it is better!

Note that I highly recommend going with netcat over this server as it is standard, battle-tested and simpler.

WebSockets support
------------------

Support of WebSockets protocol depends on the availability of the ``websockets`` python module.

To check if there is WebSocket support, you can check SpcketSrv's help message::

	$ python socketsrv.py --help
	usage: socketsrv.py [-h] [--udp-addr UDP_ADDR] [--udp-port UDP_PORT]
						[--tcp-addr TCP_ADDR] [--tcp-port TCP_PORT]
						[--ws-addr WS_ADDR] [--ws-port WS_PORT]

	Dump messages from various protocols

	optional arguments:
	  -h, --help           show this help message and exit
	  --udp-addr UDP_ADDR  Listening address for UDP (default "0.0.0.0")
	  --udp-port UDP_PORT  Listening port for UDP (default 1234)
	  --tcp-addr TCP_ADDR  Listening address for TCP (default "0.0.0.0")
	  --tcp-port TCP_PORT  Listening port for TCP (default 1234)
	  --ws-addr WS_ADDR    Listening address for WebSocket (default "0.0.0.0")
	  --ws-port WS_PORT    Listening port for WebSocket (default 1235)

If the WebSocket related options (``--ws-addr`` and ``--ws-port``) are listed, there is WebSocket support.

If you need to install ``websockets`` module, you can do so with::

	pip install websockets

Testing websockets
~~~~~~~~~~~~~~~~~~

While netcat was used as an example TCP client and can work as an UDP client, it does not support WebSockets. You can use a web browser for a quick check:

 - Launch SocketSrv as usual
 - In your favourite browser's javascript console type::

	ws = new WebSocket('ws://127.0.0.1:1235/')
	ws.send('hello mister server')

You should see the connection message when entering the first line and the message log for the second.

You will note that WebSocket's connections are described by three fields (like ``127.0.0.1:4567:/``, the last one is the path as it is a notable component of WebSocket connections.

Limitations and gotchas
~~~~~~~~~~~~~~~~~~~~~~~

SocketSrv's ``send`` command has no way to specify the message type, while WebSocket differenciates text and binary messages. ``send`` will allways send text messages. A new command ``send_bin`` may be implemented for alloowing to send binary message (and actually be able to send non-printable characters in all protocols)... but it is not done yet.

When receiving a WebSocket message, we can differenciate text message from binary ones. Text messages are printed as is while binary messages are reprensted as a python buffer (``b"..."``). It is not ideal, once again a better formating may be implemented in the future to fix it and improve other protocols.
