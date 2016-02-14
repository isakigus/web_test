# -*- coding: utf-8 -*-
from model import Observer

TEMPLATE_LOGIN = """<h1>Welcome</h1>
    <form class="form" action='/login' method='POST'>
      <input type="text" placeholder="Username" name="username">
      <input type="password" placeholder="Password" name="password">
      <button type="submit" id="login-button">Login</button>
    </form>
"""


TEMPLATE_BUTTON_EXIT = """<br/><br/>
    <form class="form" action='/exit' method='POST'>
       <input type="hidden" name="session_id" value="{session_id}">
      <button type="submit" id="exit-button">Exit</button>
    </form>
"""

HTML_BASE = """<!DOCTYPE html>
<html>
  <head>
    <title>{title}</title>
  </hea>
  <body><center>
  {content}
  </center>
  </body>
</html>
"""

USER_TEMPLATE = """<h2>Hello {user}</h2> """
FORBIDDEN_MESSAGE = """ Your are not allow to visit this url """
NOT_FOUD_MESSAGE = """ <h1>404!</h1> """

END_SESSION_MESSAGE = """<br/>
I am afraid your session has expired
<br/>
<a href="/login">go to login<a>
"""


class View(Observer):

    def __init__(self, observable):
        Observer.__init__(self, observable)

    @staticmethod
    def login():
        return HTML_BASE.format(title="welcome to log-in",
                                content=TEMPLATE_LOGIN)

    @staticmethod
    def user_page(data, page):

        username = data.get('user', {}).get('username')
        session_id = data.get('user', {}).get('session_id')

        button = TEMPLATE_BUTTON_EXIT.format(session_id=session_id)

        content = "{body}{exit}".format(
            body=USER_TEMPLATE.format(user=username),
            exit=button)

        return HTML_BASE.format(title="welcome page %s" % page,
                                content=content)

    def notify(self, observable, *msg, **kwargs):

        handler = msg[1]['handler'].handler
        route = msg[1]['route']

        if route == '/login':
            handler.send_response(200)
            handler.end_headers()
            handler.wfile.write(View.login())

        elif route.lower().startswith('/redirect'):
            handler.send_response(302)
            handler.send_header('Location', '/{}'.format(route.split('@')[1]))
            handler.end_headers()

        elif route == '/forbidden':
            handler.send_response(403)
            handler.end_headers()
            handler.wfile.write(HTML_BASE.format(title="forbidden",
                                                 content=FORBIDDEN_MESSAGE))
        elif route == '/expired':
            handler.send_response(403)
            handler.end_headers()
            handler.wfile.write(HTML_BASE.format(title="session expired",
                                                 content=END_SESSION_MESSAGE))
        elif route.lower().startswith('/user_page'):
            handler.send_response(200)
            handler.end_headers()
            handler.wfile.write(View.user_page(msg[1], route[:10]))

        else:
            handler.send_response(404)
            handler.end_headers()
            handler.wfile.write(HTML_BASE.format(title="not_found",
                                                 content=NOT_FOUD_MESSAGE))
