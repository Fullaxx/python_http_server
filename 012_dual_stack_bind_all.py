#!/usr/bin/env python3
# ./012_dual_stack_bind_all.py -p 8000
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

def run_server(port):
	global g_server
	class DualStackServer(ThreadingHTTPServer):
		address_family = socket.AF_INET6
	g_server = DualStackServer(("", port), SimpleHTTPRequestHandler)
	g_server.timeout = 1 # seconds
	print(f'Serving current directory on http://[::]:{port}')
	g_server.serve_forever(poll_interval=0.2) # seconds
	print('g_server stopped')

if __name__ == '__main__':
	parser = ArgumentParser()
	parser.add_argument('--port', '-p', type=int, required=True)
	args = parser.parse_args()

	thread = threading.Thread(target=run_server, args=(args.port,))
	thread.start()

	signal.signal(signal.SIGINT,  signal_handler)
	signal.signal(signal.SIGTERM, signal_handler)
	signal.signal(signal.SIGQUIT, signal_handler)

	while not g_shutdown:
		time.sleep(0.1)

	print('Stopping server gracefully with g_server.shutdown() ...')
	g_server.shutdown()
#	print('Stopping server abruptly with g_server.server_close() ...')
#	g_server.server_close()
	thread.join()
	print('thread has exited cleanly.')
