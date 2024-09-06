import http.server
import socketserver
import urllib.request
import urllib.error
import threading

# A handler to process HTTP requests and forward them to the actual destination
class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Parse the destination URL from the client's request
            url = self.path
            print(f"Proxying request to: {url}")
            
            # Forward the request to the actual server
            with urllib.request.urlopen(url) as response:
                content = response.read()

                # Send headers back to the client
                self.send_response(response.status)
                for header_key, header_value in response.getheaders():
                    self.send_header(header_key, header_value)
                self.end_headers()

                # Send the content back to the client
                self.wfile.write(content)
        except urllib.error.URLError as e:
            self.send_error(502, f"Bad Gateway: {e.reason}")
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")

    def do_POST(self):
        # Handle POST requests similarly
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)  # Read the incoming POST data

        try:
            url = self.path
            print(f"Proxying POST request to: {url}")

            # Forward the POST request to the actual server
            req = urllib.request.Request(url, data=post_data, method="POST")
            for key in self.headers:
                req.add_header(key, self.headers[key])

            with urllib.request.urlopen(req) as response:
                content = response.read()

                # Send headers back to the client
                self.send_response(response.status)
                for header_key, header_value in response.getheaders():
                    self.send_header(header_key, header_value)
                self.end_headers()

                # Send the content back to the client
                self.wfile.write(content)
        except urllib.error.URLError as e:
            self.send_error(502, f"Bad Gateway: {e.reason}")
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")


# Set up a multi-threaded proxy server
class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True  # This allows server threads to terminate cleanly on shutdown

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
