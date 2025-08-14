#!/usr/bin/env python3

import time
import signal
import threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

g_HOST = 'localhost'
g_PORT = 8000

g_shutdown = False
def signal_handler(sig, frame):
	global g_shutdown
	g_shutdown = True

def run_server(host, port):
	global g_server
	g_server = ThreadingHTTPServer((host, port), SimpleHTTPRequestHandler)
	g_server.timeout = 1 # seconds
	print(f'Serving current directory on http://{host}:{port}')
	g_server.serve_forever(poll_interval=0.2) # seconds
	print('Server stopped')

def terminate_server():
	global g_server
	print('Stopping server gracefully with g_server.shutdown() ...')
	g_server.shutdown()

#	print('Stopping server abruptly with g_server.server_close() ...')
#	g_server.server_close()

	thread.join()
	print('Server has exited cleanly.')

if __name__ == '__main__':
#	Run server in a thread so main program can continue
	thread = threading.Thread(target=run_server, args=(g_HOST, g_PORT))
	thread.start()

	signal.signal(signal.SIGINT,  signal_handler)
	signal.signal(signal.SIGTERM, signal_handler)
	signal.signal(signal.SIGQUIT, signal_handler)

	while not g_shutdown:
		time.sleep(0.1)

	terminate_server()
