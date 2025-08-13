#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer

class MyHandler(BaseHTTPRequestHandler):
	def do_GET(self):
#		Send response status code
		self.send_response(200)
#		Send headers
		self.send_header('Content-type', 'text/html')
		self.end_headers()
#		Send the body of the response
		self.wfile.write(b'<h1>Hello from Python HTTP server!</h1>')

if __name__ == '__main__':
	HOST = "localhost"
	PORT = 8000
	server = HTTPServer((HOST, PORT), MyHandler)
	print(f"Serving on http://{HOST}:{PORT}")
	server.serve_forever()
