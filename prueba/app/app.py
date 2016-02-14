
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

from view import View
from model import Request, Session


class GetHandler(BaseHTTPRequestHandler):

    def do_response(self, req):
        request = Request(req)
        session = Session(request)
        view = View(session)
        request.notify_observers(req)
        return

    def do_GET(self):
        self.do_response(self)

    def do_POST(self):
        self.do_response(self)


def main():
    host = 'localhost'
    port = 8080
    server = HTTPServer((host, port), GetHandler)

    print 'Starting server [ {0}:{1} ], use <Ctrl-C> to stop'.format(host, port)
    server.serve_forever()

if __name__ == '__main__':
    main()
