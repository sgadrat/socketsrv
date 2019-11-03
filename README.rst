SocketSrv
=========

One-file python server for low level protocols.

This server listens for incoming messages from multiple protocols and dumps data as it comes. It also allows to send back messages to connected clients.

It is aimed at helping when integrating a low level protocol to an application by being a ready to use server to test your client against.

Usage:
------

In a terminal, start SocketSrv::
	./socketsrv.py

In another terminal, start a client::
	nc localhost 1234

You should see a message from SocketSrv stating that a new TCP connection was made.

To send messages from nc to SocketSrv, just type it in nc's standard input.

To send messages from SocketSrv to nc, use the "send" command in SocketSrv::
	send tcp 0 hello dear tcp client

Commands list
-------------

`help`::
	Shows a little help message, protocols list and commands list

`list_clients`::
	Shows a list of all connected clients by protocol

`send`::
	Send a message to a connected client (see `send help` for more details)

Protocols list
--------------

 * TCP
 * UDP
 * WebSocket (TODO)

Advantages over netcat
----------------------

Netcat is a standard tool that works very well for testing TCP and UDP connections.

SocketSrv is a more specialized tool and features some ease of use in the case of testing low-level client developments:
 * Allows multiple connections per instance,
 * provides support for WebSockets (TODO),
 * shows more complete information about connections/disconnections of clients,
 * has an extensible interractive commands system,
 * I coded it myself, so it is better!

Note that I highly recommend going with netcat over this server as it is standard, battle-tested and simpler.
