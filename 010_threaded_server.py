#!/usr/bin/env python3

import time
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

g_HOST = 'localhost'
g_PORT = 8000

def run_server():
	global g_server
	g_server = ThreadingHTTPServer((g_HOST, g_PORT), SimpleHTTPRequestHandler)
	g_server.timeout = 1 # seconds
	print(f'Serving current directory on http://{g_HOST}:{g_PORT}')
	g_server.serve_forever(poll_interval=0.2) # seconds
	print('Server stopped')

if __name__ == '__main__':
#	Run server in a thread so main program can continue
	thread = threading.Thread(target=run_server)
	thread.start()

#	Let the server run for 5 seconds, then stop
	time.sleep(5)

	print('Stopping server gracefully with g_server.shutdown() ...')
	g_server.shutdown()

#	print('Stopping server abruptly with g_server.server_close() ...')
#	g_server.server_close()

	thread.join()
	print('Server has exited cleanly.')
