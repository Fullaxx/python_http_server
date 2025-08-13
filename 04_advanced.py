#!/usr/bin/env python3

import json
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

class MyHandler(BaseHTTPRequestHandler):

	def do_GET(self):
		if self.path == "/":
			self.send_html("""
				<h1>Welcome to My Python Server</h1>
				<p><a href="/about">About</a></p>
				<p><a href="/api">API Endpoint</a></p>
				<form method="POST" action="/">
					<label for="name">Your Name:</label>
					<input type="text" name="name">
					<input type="submit" value="Submit">
				</form>
			""")
		elif self.path == "/about":
			self.send_html("<h1>About Page</h1><p>This is a demo HTTP server in Python.</p>")
		elif self.path == "/api":
			data = {"status": "success", "message": "Hello from the API!"}
			self.send_json(data)
		else:
			self.send_error(404, "Page Not Found")

	def do_POST(self):
		if self.path == "/":
			content_length = int(self.headers.get('Content-Length', 0))
			post_data = self.rfile.read(content_length)
			parsed_data = urllib.parse.parse_qs(post_data.decode("utf-8"))
			name = parsed_data.get("name", [""])[0]
			self.send_html(f"<h1>Hello, {name}!</h1><p><a href='/'>Back</a></p>")
		else:
			self.send_error(404, "Page Not Found")

#	Utility: Send HTML response
	def send_html(self, html):
		self.send_response(200)
		self.send_header("Content-type", "text/html; charset=utf-8")
		self.end_headers()
		self.wfile.write(f"<html><body>{html}</body></html>".encode("utf-8"))

#	Utility: Send JSON response
	def send_json(self, data):
		self.send_response(200)
		self.send_header("Content-type", "application/json")
		self.end_headers()
		self.wfile.write(json.dumps(data).encode("utf-8"))

if __name__ == '__main__':
	HOST = "localhost"
	PORT = 8000
	server = HTTPServer((HOST, PORT), MyHandler)
	print(f"Serving on http://{HOST}:{PORT}")
	server.serve_forever()
