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
#  * UDP (the same way "netcat -lu" works for simulating connections) #WIP
#  * TCP #WIP
#  * Websockets #TODO
#

import select
import socket
import sys
import threading

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
			print(data)

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
				# TODO better message (with cause and client number
				# TODO remove connection from clients list
				print('< TCP connection cut')

			for socket in rcv:
				if socket is self.accepting_sock:
					client_info = socket.accept()
					self.clients.append(client_info)
					print('< new TCP connection #{}: {}'.format(len(self.clients) - 1, client_info))
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

class SocketSrv:
	"""
	Multi-protocol server
	"""
	def __init__(self, config):
		self.udp_server = UdpServer((config['udp']['addr'], config['udp']['port']))
		self.tcp_server = TcpServer((config['tcp']['addr'], config['tcp']['port']))

	def cmd_help(self, args):
		"""
		Print commands list
		"""
		#TODO
		print('Read the fucking source')

	def cmd_send(self, args):
		if len(args) == 0 or args[0] == 'help':
			print('send <protocol> <client-num> <message>')
			print('\t<protocol> shall be "udp"')
			print('\t<client-num> index of the client in protocol\'s clients list')
			print('\t<message> anything to send to the client (may contain spaces)')
		elif args[0] == 'udp':
			client_num = int(args[1])
			message = (' '.join(args[2:]) + '\n').encode('utf-8')
			self.udp_server.sock.sendto(message, self.udp_server.clients[client_num])
			print('> sent datagram to UDP session #{}: {}'.format(client_num, message))

	def cmd_dbg(self, args):
		"""
		Developper's command, printing esotheric results that only gurus can understand
		"""
		print(str(self.udp_server.clients))

	def run(self):
		udp_server_thread = threading.Thread(target=self.udp_server.run)
		udp_server_thread.daemon = True
		udp_server_thread.start()
		tcp_server_thread = threading.Thread(target=self.tcp_server.run)
		tcp_server_thread.daemon = True
		tcp_server_thread.start()

		while True:
			line = sys.stdin.readline()
			if line == '':
				break
			cmd = line[:-1].split(' ')

			if hasattr(self, 'cmd_{}'.format(cmd[0])):
				getattr(self, 'cmd_{}'.format(cmd[0]))(cmd[1:])
			else:
				print('unknown command {}'.format(cmd[0]))
				self.cmd_help([])

		udp_server_thread.join()

if __name__ == "__main__":
	srv = SocketSrv({
		'udp': {'addr':'0.0.0.0', 'port':1234},
		'tcp': {'addr':'0.0.0.0', 'port':1234}
	})
	srv.run()
