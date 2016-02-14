import urlparse
import datetime
import time

session_time = datetime.datetime.now
FiveMinutes = datetime.timedelta(seconds=20)


class Observable:

    def __init__(self):
        self.__observers = []

    def register_observer(self, observer):
        self.__observers.append(observer)

    def notify_observers(self, *args, **kwargs):
        for observer in self.__observers:
            observer.notify(self, *args, **kwargs)


class Observer:

    def __init__(self, observable):
        observable.register_observer(self)

    def notify(self, observable, *args, **kwargs):
        print('Got', args, kwargs, 'From', observable)


class Session(Observable, Observer):

    USERS = [{'username': 'user1',
              'password': '1',
              'last_action': None,
              'rol': ['PAG_1'],
              'home_page': 'user_page1'
              },

             {'username': 'user2',
              'password': '2',
              'last_action': None,
              'rol': ['PAG_2'],
              'home_page': 'user_page2'
              },
             {'username': 'user3',
              'password': '3',
              'last_action': None,
              'rol': ['PAG_3'],
                 'home_page': 'user_page3'
              },
             {'username': 'user4',
              'password': '4',
              'last_action': None,
              'rol': ['PAG_1', 'PAG_3'],
              'home_page': 'user_page1'},
             ]

    ROLES_MAPPING = {
        'PAG_1': 'user_page1',
        'PAG_2': 'user_page2',
        'PAG_3': 'user_page3'
    }

    def __init__(self, observable):
        Observable.__init__(self)
        Observer.__init__(self, observable)

    def notify(self, observable, *args, **kwargs):

        session_id, route = self.get_session_id(observable.parsed_path)

        if observable.handler.command == 'POST':
            params = self.parse_post(observable.handler)

            if route == '/exit':
                session_id = params.get('session_id')
                if session_id:
                    user = self.get_user_by_session_id(session_id)
                    if user:
                        del user['session_id']
                        user['last_action'] = None
                        route, session_id = '/login', None

        user, route = self.check_session_id(session_id, route)

        if route == '/login' and observable.handler.command == 'POST':
            user, route = self.check_user_id(params, route)

        message = {'route': route, 'user': user, 'handler': observable}

        self.notify_observers(self, message)

    def check_role(self, route, rol):

        if route == '/exit':
            return True

        for role in rol:
            if Session.ROLES_MAPPING[role] in route:
                return True
        return False

    def get_user_by_session_id(self, session_id):

        for user in Session.USERS:
            if session_id == user.get('session_id'):
                return user

        return None

    def check_session_id(self, session_id, route):

        if not session_id:
            return None, '/login'

        user = self.get_user_by_session_id(session_id)

        if user:
            if self.check_role(route, user.get('rol')):
                if user['last_action'] + FiveMinutes < session_time():
                    return user, '/expired'
                else:
                    user['last_action'] = session_time()
                    return user, route
            else:
                return user, '/forbidden'
        else:
            return None, '/login'

    def check_user_id(self, params, route):

        for user in Session.USERS:
            if (params.get('username') == user.get('username') and
                    params.get('password') == user.get('password')):
                user['last_action'] = session_time()
                user['session_id'] = self.create_session_id()
                route = '/redirect@{0}?session_id={1}'.format(
                    user.get('home_page'), user['session_id'])
                return user, route

        return None, '/login'

    def create_session_id(self):
        timestamp2 = time.mktime(session_time().timetuple())
        return str(int(timestamp2))

    def get_session_id(self, path):

        session_id = None

        if path.query and 'session_id' in path.query:
            for item in path.query.split('&'):
                if item.startswith('session_id'):
                    session_id = item[len('session_id')+1:]

        return session_id, path.path

    def parse_params(self, params_string):
        params = {}

        for item in params_string.split('&'):
            key, value = item.split('=')
            params.update({key: value.rstrip()})

        return params

    def get_headers(self, handler):
        headers = {}
        for name, value in handler.headers.items():
            headers.update({name: value.rstrip()})

        return headers

    def parse_post(self, req_obj):
        headers = self.get_headers(req_obj)
        length = int(headers['content-length'])
        return self.parse_params(req_obj.rfile.read(length))


class Request(Observable):

    def __init__(self, req_obj):
        Observable.__init__(self)
        self.handler = req_obj
        self.parsed_path = urlparse.urlparse(self.handler.path)

    def __str__(self):

        message_parts = [
            'CLIENT VALUES:',
            'client_address=%s (%s)' % (self.handler .client_address,
                                        self.handler .address_string()),
            'command=%s' % self.handler.command,
            'path=%s' % self.handler.path,
            'real path=%s' % self.parsed_path.path,
            'query=%s' % self.parsed_path.query,
            'request_version=%s' % self.handler.request_version,
            '',
            'SERVER VALUES:',
            'server_version=%s' % self.handler.server_version,
            'sys_version=%s' % self.handler.sys_version,
            'protocol_version=%s' % self.handler.protocol_version,
            '',
            'HEADERS RECEIVED:',
        ]
        for name, value in sorted(self.handler.headers.items()):
            message_parts.append('%s=%s' % (name, value.rstrip()))
        message_parts.append('')
        message = '\r\n'.join(message_parts)

        return message
