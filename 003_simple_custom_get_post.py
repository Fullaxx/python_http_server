#!/usr/bin/env python3

import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

class MyHandler(BaseHTTPRequestHandler):
	def do_GET(self):
#		Respond with a simple HTML form
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()

		html = """
		<html>
		<body>
			<h1>Simple Python HTTP Server</h1>
			<form method="POST">
				<label for="name">Your Name:</label>
				<input type="text" name="name">
				<input type="submit" value="Submit">
			</form>
		</body>
		</html>
		"""
		self.wfile.write(html.encode("utf-8"))

	def do_POST(self):
#		Get the length of the POST data
		content_length = int(self.headers.get('Content-Length', 0))
#		Read the POST data
		post_data = self.rfile.read(content_length)
#		Parse it
		parsed_data = urllib.parse.parse_qs(post_data.decode("utf-8"))

#		Extract the name field (list with one element)
		name = parsed_data.get("name", [""])[0]

#		Send a response back
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()

		response_html = f"""
		<html>
		<body>
			<h1>Hello, {name}!</h1>
			<a href="/">Back</a>
		</body>
		</html>
		"""
		self.wfile.write(response_html.encode("utf-8"))

if __name__ == '__main__':
	HOST = "localhost"
	PORT = 8000
	server = HTTPServer((HOST, PORT), MyHandler)
	print(f"Serving on http://{HOST}:{PORT}")
	server.serve_forever()
