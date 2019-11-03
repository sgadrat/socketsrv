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
	Send a message to a connected client (see ``send help`` for more details)

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
==================

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
