#!/usr/bin/env python3

import os
import json
import mimetypes
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

STATIC_DIR = 'static'  # Folder for static files

class MyHandler(BaseHTTPRequestHandler):

	def do_GET(self):
#		Check if request is for a static file
		if self.path.startswith("/static/"):
			return self.serve_static(self.path[1:])  # remove leading "/"

#		Handle normal routes
		if self.path == "/":
			self.send_html("""
				<h1>Welcome to My Python Server</h1>
				<link rel="stylesheet" href="/static/style.css">
				<p><a href="/about">About</a></p>
				<p><a href="/api">API Endpoint</a></p>
				<form method="POST" action="/">
					<label>Your Name:</label>
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

#	Serve HTML content
	def send_html(self, html):
		self.send_response(200)
		self.send_header("Content-type", "text/html; charset=utf-8")
		self.end_headers()
		self.wfile.write(f"<html><body>{html}</body></html>".encode("utf-8"))

#	Serve JSON response
	def send_json(self, data):
		self.send_response(200)
		self.send_header("Content-type", "application/json")
		self.end_headers()
		self.wfile.write(json.dumps(data).encode("utf-8"))

#	Serve static files
	def serve_static(self, file_path):
		full_path = os.path.join(STATIC_DIR, os.path.relpath(file_path, "static"))

		if not os.path.isfile(full_path):
			self.send_error(404, "File Not Found")
			return

		mime_type, _ = mimetypes.guess_type(full_path)
		if not mime_type:
			mime_type = "application/octet-stream"

		self.send_response(200)
		self.send_header("Content-type", mime_type)
		self.end_headers()

		with open(full_path, "rb") as f:
			self.wfile.write(f.read())

if __name__ == '__main__':
	HOST = "localhost"
	PORT = 8000
	server = HTTPServer((HOST, PORT), MyHandler)
	print(f"Serving on http://{HOST}:{PORT}")
	server.serve_forever()
