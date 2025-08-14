#!/usr/bin/env python3

import os
import re
import json
import mimetypes
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

STATIC_DIR = 'static'  # Folder for static files

# --- Minimal HTML template renderer ---
def render_template(title, content):
	return f"""
	<!DOCTYPE html>
	<html>
	<head>
		<meta charset="utf-8">
		<title>{title}</title>
		<link rel="stylesheet" href="/static/style.css">
	</head>
	<body>
		<header>
			<nav>
				<a href="/">Home</a> |
				<a href="/about">About</a> |
				<a href="/search?term=python">Search Example</a> |
				<a href="/api">API</a> |
				<a href="/user/42">User Example</a>
			</nav>
		</header>
		<main>
			{content}
		</main>
	</body>
	</html>
	"""

class MyHandler(BaseHTTPRequestHandler):

	def do_GET(self):
#		Serve static files
		if self.path.startswith("/static/"):
			return self.serve_static(self.path[1:])

#		Parse URL & query parameters
		parsed_url = urllib.parse.urlparse(self.path)
		path = parsed_url.path
		query_params = urllib.parse.parse_qs(parsed_url.query)

#		--- Route matching ---
		if path == "/":
			html = render_template("Home", """
				<h1>Welcome to My Python Server</h1>
				<form method="POST" action="/">
					<label>Your Name:</label>
					<input type="text" name="name">
					<input type="submit" value="Submit">
				</form>
			""")
			self.send_html(html)
		elif path == "/about":
			html = render_template("About", "<h1>About Page</h1><p>This is a demo HTTP server in Python.</p>")
			self.send_html(html)
		elif path == "/search":
			term = query_params.get("term", [""])[0]
			html = render_template("Search", f"<h1>Search Results for '{term}'</h1><p>No real results — just a demo!</p>")
			self.send_html(html)
		elif path == "/api":
			data = {"status": "success", "message": "Hello from the API!"}
			self.send_json(data)
		# Path parameter example: /user/<id>
		elif re.fullmatch(r"/user/\d+", path):
			user_id = path.split("/")[-1]
			html = render_template("User Page", f"<h1>User ID: {user_id}</h1>")
			self.send_html(html)
		else:
			self.send_error(404, "Page Not Found")

	def do_POST(self):
		if self.path == "/":
			content_length = int(self.headers.get('Content-Length', 0))
			post_data = self.rfile.read(content_length)
			parsed_data = urllib.parse.parse_qs(post_data.decode("utf-8"))
			name = parsed_data.get("name", [""])[0]
			html = render_template("Greeting", f"<h1>Hello, {name}!</h1><p><a href='/'>Back</a></p>")
			self.send_html(html)
		else:
			self.send_error(404, "Page Not Found")

#	--- Helpers ---
	def send_html(self, html):
		self.send_response(200)
		self.send_header("Content-type", "text/html; charset=utf-8")
		self.end_headers()
		self.wfile.write(html.encode("utf-8"))

	def send_json(self, data):
		self.send_response(200)
		self.send_header("Content-type", "application/json")
		self.end_headers()
		self.wfile.write(json.dumps(data).encode("utf-8"))

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
