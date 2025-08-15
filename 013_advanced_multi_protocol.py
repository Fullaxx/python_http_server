#!/usr/bin/env python3
# ./013_advanced_multi_protocol.py -4 "*" -6 "*" -p 8000
# curl http://127.0.0.1:8000/
# curl -g http://[::1]:8000/

import sys
import time
import signal
import socket
import threading

from argparse import ArgumentParser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

def eprint(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)

def bailmsg(*args, **kwargs):
	eprint(*args, **kwargs)
	sys.exit(1)

g_shutdown = False
def signal_handler(sig, frame):
	global g_shutdown
	g_shutdown = True

def run_server_ipv4(host, port):
	global g_s4
	class DualStackServer(ThreadingHTTPServer):
		address_family = socket.AF_INET
	g_s4 = DualStackServer((host, port), SimpleHTTPRequestHandler)
	g_s4.timeout = 1 # seconds
	if host == "":
		print(f'Serving current directory on http://*:{port}')
	else:
		print(f'Serving current directory on http://{host}:{port}')
	g_s4.serve_forever(poll_interval=0.2) # seconds
	print('g_s4 stopped')

def run_server_ipv6(host, port):
	global g_s6
	class DualStackServer(ThreadingHTTPServer):
		address_family = socket.AF_INET6
		def server_bind(self):
			self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
			super().server_bind()
	g_s6 = DualStackServer((host, port), SimpleHTTPRequestHandler)
	g_s6.timeout = 1 # seconds
	if host == "" or host == "::": host = "[::]"
	print(f'Serving current directory on http://{host}:{port}')
	g_s6.serve_forever(poll_interval=0.2) # seconds
	print('g_s6 stopped')

if __name__ == '__main__':
	parser = ArgumentParser()
	parser.add_argument('--port', '-p', type=int, required=True)
	parser.add_argument('--ipv4', '-4', type=str, required=False)
	parser.add_argument('--ipv6', '-6', type=str, required=False)
	args = parser.parse_args()

	if (not args.ipv4) and (not args.ipv6):
		bailmsg("I need a protocol family (Fix with -4/-6)")

	if args.ipv4:
		ipv4_host = "0.0.0.0" if args.ipv4 == "*" else args.ipv4
		t4 = threading.Thread(target=run_server_ipv4, args=(ipv4_host, args.port))
		t4.start()

	if args.ipv6:
		ipv6_host = "::" if args.ipv6 == "*" else args.ipv6
		t6 = threading.Thread(target=run_server_ipv6, args=(ipv6_host, args.port))
		t6.start()

	signal.signal(signal.SIGINT,  signal_handler)
	signal.signal(signal.SIGTERM, signal_handler)
	signal.signal(signal.SIGQUIT, signal_handler)

	while not g_shutdown:
		time.sleep(0.1)

	if args.ipv4:
		print('Stopping server gracefully with g_s4.shutdown() ...')
		g_s4.shutdown()
#		print('Stopping server abruptly with g_s4.server_close() ...')
#		g_s4.server_close()
		t4.join()
		print('t4 has exited cleanly.')

	if args.ipv6:
		print('Stopping server gracefully with g_s6.shutdown() ...')
		g_s6.shutdown()
#		print('Stopping server abruptly with g_s6.server_close() ...')
#		g_s6.server_close()
		t6.join()
		print('t6 has exited cleanly.')
