#!/usr/bin/env python3

import os
import re
import json
import base64
import mimetypes
import urllib.parse

from functools import wraps
from http.server import BaseHTTPRequestHandler, HTTPServer

STATIC_DIR = "static"
ROUTES = {"GET": [], "POST": []}
USERNAME = "admin"
PASSWORD = "secret"  # Change to your desired password

# --- Route decorator ---
def route(path, methods=["GET"]):
	def decorator(func):
		for method in methods:
			ROUTES[method.upper()].append((path, func))
		return func
	return decorator

# --- Basic auth decorator ---
def require_basic_auth(func):
	def wrapper(handler, *args, **kwargs):
		auth_header = handler.headers.get("Authorization")
		if not auth_header or not auth_header.startswith("Basic "):
			return handler.request_auth()
		try:
			decoded = base64.b64decode(auth_header.split(" ")[1]).decode("utf-8")
			user, pwd = decoded.split(":", 1)
		except Exception:
			return handler.request_auth()

		if user == USERNAME and pwd == PASSWORD:
			return func(handler, *args, **kwargs)
		else:
			return handler.request_auth()
	return wrapper

# --- Minimal HTML template ---
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
				<a href="/search?term=python">Search</a> |
				<a href="/api">API</a> |
				<a href="/user/42">User Example</a> |
				<a href="/restricted">Restricted</a>
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
		if self.path.startswith("/static/"):
			return self.serve_static(self.path[1:])

		parsed_url = urllib.parse.urlparse(self.path)
		path = parsed_url.path
		query_params = urllib.parse.parse_qs(parsed_url.query)

		for route_pattern, handler in ROUTES["GET"]:
			match = self.match_route(route_pattern, path)
			if match is not None:
				return handler(self, **match, query=query_params)

		self.send_error(404, "Page Not Found")

	def do_POST(self):
		parsed_url = urllib.parse.urlparse(self.path)
		path = parsed_url.path

		content_length = int(self.headers.get('Content-Length', 0))
		post_data = urllib.parse.parse_qs(self.rfile.read(content_length).decode("utf-8"))

		for route_pattern, handler in ROUTES["POST"]:
			match = self.match_route(route_pattern, path)
			if match is not None:
				return handler(self, **match, form=post_data)

		self.send_error(404, "Page Not Found")

	def match_route(self, pattern, path):
		regex_pattern = re.sub(r"<(\w+)>", r"(?P<\1>[^/]+)", pattern)
		match = re.fullmatch(regex_pattern, path)
		return match.groupdict() if match else None

	# --- Response helpers ---
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

	def request_auth(self):
		self.send_response(401)
		self.send_header("WWW-Authenticate", 'Basic realm="Restricted Area"')
		self.send_header("Content-type", "text/html; charset=utf-8")
		self.end_headers()
		self.wfile.write(b"<h1>401 Unauthorized</h1><p>Authentication required.</p>")

# --- Routes ---
@route("/", methods=["GET"])
def home(handler, query):
	html = render_template("Home", """
		<h1>Welcome to My Python Server</h1>
		<form method="POST" action="/">
			<label>Your Name:</label>
			<input type="text" name="name">
			<input type="submit" value="Submit">
		</form>
	""")
	handler.send_html(html)

@route("/", methods=["POST"])
def home_post(handler, form):
	name = form.get("name", [""])[0]
	html = render_template("Greeting", f"<h1>Hello, {name}!</h1><p><a href='/'>Back</a></p>")
	handler.send_html(html)

@route("/about", methods=["GET"])
def about(handler, query):
	html = render_template("About", "<h1>About Page</h1><p>This is a demo HTTP server in Python.</p>")
	handler.send_html(html)

@route("/search", methods=["GET"])
def search(handler, query):
	term = query.get("term", [""])[0]
	html = render_template("Search", f"<h1>Search Results for '{term}'</h1><p>No real results — just a demo!</p>")
	handler.send_html(html)

@route("/api", methods=["GET"])
def api(handler, query):
	data = {"status": "success", "message": "Hello from the API!"}
	handler.send_json(data)

@route("/user/<id>", methods=["GET"])
def user_page(handler, id, query):
	html = render_template("User Page", f"<h1>User ID: {id}</h1>")
	handler.send_html(html)

@route("/restricted", methods=["GET"])
@require_basic_auth
def restricted(handler, query):
	html = render_template("Restricted", "<h1>Welcome to the restricted area!</h1>")
	handler.send_html(html)

if __name__ == '__main__':
	HOST = "localhost"
	PORT = 8000
	server = HTTPServer((HOST, PORT), MyHandler)
	print(f"Serving on http://{HOST}:{PORT}")
	server.serve_forever()
