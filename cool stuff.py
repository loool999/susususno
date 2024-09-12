import http.server
import socketserver
import urllib.request
import urllib.parse
import urllib.error
import threading

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Check if the request path is a full URL or a relative one
            if self.path.startswith("http://") or self.path.startswith("https://"):
                url = self.path
            else:
                url = f"http://{self.headers['Host']}{self.path}"

            print(f"Proxying GET request to: {url}")

            # Create the request object and forward the headers from the client
            req = urllib.request.Request(url)
            for header in self.headers:
                if header.lower() != 'host':
                    req.add_header(header, self.headers[header])

            # Forward the request to the destination server
            with urllib.request.urlopen(req) as response:
                content = response.read()

                # Send the status code and headers back to the client
                self.send_response(response.status)
                for header_key, header_value in response.getheaders():
                    self.send_header(header_key, header_value)
                self.end_headers()

                # Write the content to the client
                self.wfile.write(content)
        except urllib.error.HTTPError as e:
            self.send_error(e.code, f"HTTP Error: {e.reason}")
        except urllib.error.URLError as e:
            self.send_error(502, f"Bad Gateway: {e.reason}")
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        try:
            if self.path.startswith("http://") or self.path.startswith("https://"):
                url = self.path
            else:
                url = f"http://{self.headers['Host']}{self.path}"

            print(f"Proxying POST request to: {url}")

            req = urllib.request.Request(url, data=post_data, method="POST")
            for header in self.headers:
                if header.lower() != 'host':
                    req.add_header(header, self.headers[header])

            # Forward the POST request to the actual server
            with urllib.request.urlopen(req) as response:
                content = response.read()

                self.send_response(response.status)
                for header_key, header_value in response.getheaders():
                    self.send_header(header_key, header_value)
                self.end_headers()

                self.wfile.write(content)
        except urllib.error.HTTPError as e:
            self.send_error(e.code, f"HTTP Error: {e.reason}")
        except urllib.error.URLError as e:
            self.send_error(502, f"Bad Gateway: {e.reason}")
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")

# Set up a multi-threaded proxy server
class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

if __name__ == "__main__":
    PORT = 8080
    server_address = ("", PORT)

    # Create and start the proxy server
    httpd = ThreadingHTTPServer(server_address, ProxyHandler)
    print(f"Serving HTTP Proxy on port {PORT}")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        print("Proxy server stopped.")
