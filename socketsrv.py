#!/bin/env python3

#
# The goald of this project is to be a one-file multi-protocol server that can
# be used while developping network applications.
#
# The program should listen for various protocols, logging about established
# connections and received payloads. It also should allow to send messages
# to connected clients.
#
# Supported protocols:
#  * UDP (the same way "netcat -lu" works for simulating connections) #WIP
#  * TCP #TODO
#  * Websockets #TODO
#

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

class SocketSrv:
	"""
	Multi-protocol server
	"""
	def __init__(self, udp_config):
		self.udp_server = UdpServer((udp_config['addr'], udp_config['port']))

	def cmd_help(self, args):
		"""
		Print commands list
		"""
		#TODO
		print('Read the fucking source')

	def cmd_send(self, args):
		if args[0] == 'help':
			print('send <protocol> <client-num> <message>')
			print('\t<protocol> shall be "udp"')
			print('\t<client-num> index of the client in protocol\'s clients list')
			print('\t<message> anything to send to the client (may contain spaces)')
		elif args[0] == 'udp':
			client_num = int(args[1])
			self.udp_server.sock.sendto((' '.join(args[2:]) + '\n').encode('utf-8'), self.udp_server.clients[client_num])

	def cmd_dbg(self, args):
		"""
		Developper's command, printing esotheric results that only gurus can understand
		"""
		print(str(self.udp_server.clients))

	def run(self):
		udp_server_thread = threading.Thread(target=self.udp_server.run)
		udp_server_thread.daemon = True
		udp_server_thread.start()

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
	srv = SocketSrv({'addr':'0.0.0.0', 'port':1234})
	srv.run()
