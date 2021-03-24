#!/bin/env python3

#
# The goal of this project is to be a one-file multi-protocol server that can
# be used while developping network applications.
#
# The program should listen for various protocols, logging about established
# connections and received payloads. It also should allow to send messages
# to connected clients.
#
# Supported protocols:
#  * UDP (the same way "netcat -lu" works for simulating connections)
#  * TCP
#  * Websockets
#

import argparse
import select
import socket
import sys
import threading

readline_available = False
try:
	import readline # Keep it even if it seems unused, it improves input()
	readline_available = True
except ModuleNotFoundError:
	try:
		from pyreadline import Readline
		readline = Readline()
		readline_available = True
	except ModuleNotFoundError:
		pass

websockets_available = False
try:
	import asyncio
	import websockets
	websockets_available = True
except ModuleNotFoundError:
	pass

class UdpServer:
	"""
	Server handling UDP protocol
	"""
	def __init__(self, listen_addr):
		"""
		param listen_addr Tuple (str addr, int port)
		"""
		self.clients = []
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.bind(listen_addr)
		self._max_payload_size = 1024

	def run(self):
		while True:
			data, addr = self.sock.recvfrom(self._max_payload_size)
			if addr not in self.clients:
				self.clients.append(addr)
				client_num = self.clients.index(addr)
				print('< new UDP session #{}: {}'.format(client_num, self.get_client_desc(client_num)))
			client_num = self.clients.index(addr)
			print('< received datagram from UDP session #{}: {}'.format(client_num, data))

	def send(self, message, client_num):
		if client_num < len(self.clients):
			payload = message
			if isinstance(message, str):
				payload = message.encode('utf-8')

			self.sock.sendto(payload, self.clients[client_num])
			print('> sent datagram to UDP session #{}: {}'.format(client_num, message))
		else:
			raise Exception('unknown client #{}'.format(client_num))

	def get_client_desc(self, client_num):
		return '{}:{}'.format(self.clients[client_num][0], self.clients[client_num][1])

class TcpServer:
	"""
	Server handling TCP protocol
	"""
	def __init__(self, listen_addr):
		"""
		param listen_addr Tuple (str addr, int port)
		"""
		self.accepting_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.accepting_sock.bind(listen_addr)
		self.accepting_thread = None
		self.clients = []
		self._max_payload_size = 1024

	def client_num_from_socket(self, socket):
		client_num = None
		for client_info in self.clients:
			if client_info is not None and client_info[0] is socket:
				client_num = self.clients.index(client_info)
				break
		return client_num

	def run(self):
		self.accepting_sock.listen()
		while True:
			sockets_list = [self.accepting_sock] + [x[0] for x in self.clients if x is not None] # List containing the accepting socket and all client sockets
			rcv, snd, error = select.select(sockets_list, [], sockets_list)

			for socket in error:
				client_num = self.client_num_from_socket(socket)
				assert client_num is not None
				print('< TCP connection #{} cut'.format(client_num))
				self.clients[client_num] = None

			for socket in rcv:
				if socket is self.accepting_sock:
					client_info = socket.accept()
					client_num = len(self.clients)
					self.clients.append(client_info)
					print('< new TCP connection #{}: {}'.format(client_num, self.get_client_desc(client_num)))
				else:
					client_num = self.client_num_from_socket(socket)
					assert client_num is not None

					data = socket.recv(self._max_payload_size)
					if len(data) == 0:
						print('< end of TCP connection #{}'.format(client_num))
						try:
							self.clients[client_num][0].close()
						except Exception:
							pass
						self.clients[client_num] = None
					else:
						print('< received payload on TCP connection #{}: {}'.format(client_num, data))

	def send(self, message, client_num):
		if client_num < len(self.clients):
			client_info = self.clients[client_num]
			if client_info is None:
				raise Exception('try to write on closed TCP connection #{}'.format(client_num))

			payload = message
			if isinstance(message, str):
				payload = message.encode('utf-8')

			client_socket = client_info[0]
			client_socket.send(payload)
			print('> sent payload to TCP connection #{}: {}'.format(client_num, message))
		else:
			raise Exception('try to write on unknown TCP connection #{}'.format(client_num))

	def get_client_desc(self, client_num):
		client_info = self.clients[client_num]
		if client_info is None:
			return 'closed connection'
		return '{}:{}'.format(client_info[1][0], client_info[1][1])

class WsServer:
	"""
	Server handling WebSocket protocol
	"""
	def __init__(self, listen_addr):
		"""
		param listen_addr Tuple (str addr, int port)
		"""
		self.clients = []
		self.listen_addr = listen_addr

	def run(self):
		# Ensure there is an event loop for the current thread then create and start the websocket server
		asyncio.set_event_loop(asyncio.new_event_loop())
		server_task = websockets.serve(self.handle_connection, self.listen_addr[0], self.listen_addr[1])
		asyncio.get_event_loop().run_until_complete(server_task)
		asyncio.get_event_loop().run_forever()

	async def handle_connection(self, socket, path):
		# Register client
		client_num = len(self.clients)
		self.clients.append((socket, path))
		assert len(self.clients) == client_num + 1, "race condition on websocket client connection, should be fixed by a lock"
		print('< new WebSocket connection #{}: {}'.format(client_num, self.get_client_desc(client_num)))

		# Handle messages
		while True:
			data = await socket.recv()
			print('< Received message on WebSocket connection #{}: {}'.format(client_num, data))

		# Unregister client
		self.clients[client_num] = None

	def send(self, message, client_num):
		if client_num < len(self.clients):
			client_info = self.clients[client_num]
			if client_info is None:
				raise Exception('try to write on closed WebSocket connection #{}'.format(client_num))
			client_socket = client_info[0]
			asyncio.run(client_socket.send(message))
			print('> sent message to WebSocket connection #{}: {}'.format(client_num, message))
		else:
			raise Exception('try to write on unknown WebSocket connection #{}'.format(client_num))

	def get_client_desc(self, client_num):
		client_info = self.clients[client_num]
		remote_addr = client_info[0].remote_address
		path = client_info[1]
		return '{}:{}:{}'.format(remote_addr[0], remote_addr[1], path)

class SocketSrv:
	"""
	Multi-protocol server
	"""
	def __init__(self, config):
		self.servers = {
			'udp': UdpServer((config['udp']['addr'], config['udp']['port'])),
			'tcp': TcpServer((config['tcp']['addr'], config['tcp']['port'])),
		}
		if websockets_available:
			self.servers['ws'] = WsServer((config['ws']['addr'], config['ws']['port']))

	def cmd_help(self, args):
		"""
		Print commands list
		"""
		print('Server listening on multiple protocol, printing messages as they come')
		print('and allowing to interract with clients with interactive commands.')
		print('')

		print('Handled protocols:')
		for protocol in self.servers:
			print('\t{}'.format(protocol))
		print('')

		print('Commands list:')
		for attr in dir(self):
			if attr[:4] == 'cmd_':
				print('\t{}'.format(attr[4:]))

	def cmd_send(self, args):
		if len(args) < 2 or args[0] == 'help':
			print('send <protocol> <client-num> <message>')
			print('\t<protocol> one of the handled protocols')
			print('\t<client-num> index of the client in protocol\'s clients list')
			print('\t<message> anything to send to the client (may contain spaces)')
		elif args[0] in self.servers:
			client_num = int(args[1])
			message = ' '.join(args[2:]) + '\n'
			try:
				self.servers[args[0]].send(message, client_num)
			except Exception as e:
				print('X {}'.format(e))
		else:
			print('X unknown protocol {}'.format(args[0]))

	def cmd_sendb(self, args):
		if len(args) < 2 or args[0] == 'help':
			print('sendb <protocol> <client-num> <message>')
			print('\t<protocol> one of the handled protocols')
			print('\t<client-num> index of the client in protocol\'s clients list')
			print('\t<message> hexadecimal representation of data to send to the client (spaces are ignored)')
		elif args[0] in self.servers:
			client_num = int(args[1])
			message_hex = ' '.join(args[2:])
			message = bytes.fromhex(message_hex)
			try:
				self.servers[args[0]].send(message, client_num)
			except Exception as e:
				print('X {}'.format(e))
		else:
			print('X unknown protocol {}'.format(args[0]))

	def cmd_list_clients(self, args):
		if len(args) > 0 and args[0] == 'help':
			print('list_clients')
			print('\tLists clients for each protocol')
		else:
			for protocol in self.servers:
				server = self.servers[protocol]
				print('{}:'.format(protocol))
				if len(server.clients) > 0:
					for client_num in range(len(server.clients)):
						print('\t#{}: {}'.format(client_num, server.get_client_desc(client_num)))
				else:
					print('\tNo client')

	def run(self):
		server_threads = []
		for protocol in self.servers:
			server_thread = threading.Thread(target=self.servers[protocol].run)
			server_thread.daemon = True
			server_thread.start()
			server_threads.append(server_thread)

		while True:
			line = input()
			if line == '':
				continue
			cmd = line.split(' ')

			if hasattr(self, 'cmd_{}'.format(cmd[0])):
				try:
					getattr(self, 'cmd_{}'.format(cmd[0]))(cmd[1:])
				except Exception as e:
					print('X {}'.format(e))
			else:
				print('unknown command {}'.format(cmd[0]))
				self.cmd_help([])

		for server_thread in server_threads:
			server_thread.join()

if __name__ == "__main__":
	if not readline_available:
		print('Notice: no readline implementation found. The prompt will be rough. Install readline or pyreadline to fix the problem.\n')

	parser = argparse.ArgumentParser(description='Dump messages from various protocols')
	parser.add_argument('--udp-addr', default='0.0.0.0', help='Listening address for UDP (default "0.0.0.0")')
	parser.add_argument('--udp-port', default=1234, type=int, help='Listening port for UDP (default 1234)')
	parser.add_argument('--tcp-addr', default='0.0.0.0', help='Listening address for TCP (default "0.0.0.0")')
	parser.add_argument('--tcp-port', default=1234, type=int, help='Listening port for TCP (default 1234)')
	if websockets_available:
		parser.add_argument('--ws-addr', default='0.0.0.0', help='Listening address for WebSocket (default "0.0.0.0")')
		parser.add_argument('--ws-port', default=1235, type=int, help='Listening port for WebSocket (default 1235)')
	args = parser.parse_args()

	srv = SocketSrv({
		'udp': {'addr':args.udp_addr, 'port':args.udp_port},
		'tcp': {'addr':args.tcp_addr, 'port':args.tcp_port},
		'ws': {'addr':args.ws_addr, 'port':args.ws_port} if websockets_available else None
	})

	try:
		srv.run()
	except (EOFError, KeyboardInterrupt):
		# EOFError: stdin was closed
		# KeyboardInterrupt: ctrl+c
		pass
