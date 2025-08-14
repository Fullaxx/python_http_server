#!/usr/bin/env python3

from http.server import SimpleHTTPRequestHandler, HTTPServer

if __name__ == '__main__':
	HOST = "localhost"
	PORT = 8000
	server = HTTPServer((HOST, PORT), SimpleHTTPRequestHandler)
	print(f'Serving current directory on http://{HOST}:{PORT}')
	server.serve_forever()
