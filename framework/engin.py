# page controller
def index_view(request):
    print(request)
    return '200 OK', [b'index_view']


def contacts_view(request):
    print(request)
    return '200 OK', [b'contacts_view']


def services_view(request):
    print(request)
    return '200 OK', [b'services_view']


def error_404_view(request):
    print(request)
    return '404 ERROR', [b'error_404_view']


class Other:
    def __call__(self, request):
        print(request)
        return '200 OK', [b'<h1>other_view</h1>']


routes = {
    '/': index_view,
    '/contacts/': contacts_view,
    '/services/': services_view,
    '/other/': Other()
}


# Front controllers

def secret_front(request):
    request['secret'] = 'some secret'


def other_front(request):
    request['other_key'] = 'key'


fronts = [secret_front, other_front]


class Application():
    def __init__(self, routes: dict, fronts: list):
        self.routes = routes
        self.fronts = fronts

    def __call__(self, environ, start_response):
        # print(environ)
        # print(type(environ))
        print('work')

        path = environ['PATH_INFO']
        if len(path) > 1:
            if path[-1:] != '/':
                path = path + '/'

        if path in self.routes:
            print(f'-----------> {self.routes[path]}')
            view = self.routes[path]
        else:
            view = error_404_view
        request = {}

        for front in self.fronts:
            front(request)

        code, body = view(request)
        start_response(code, [('Content-Type', 'text/html')])
        # if type(body) is list:
        #     return body[0].encode('utf-8')
        # return body.encode('utf-8')
        return body

        # if path == '/':
        #     start_response('200 OK', [('Content-Type', 'text/html')])
        #     return [f'Main Page - {path}'.encode('utf-8')]
        #
        # elif path == '/index':
        #     start_response('200 OK', [('Content-Type', 'text/html')])
        #     return [f'Page -  {path}'.encode('utf-8')]
        #
        # elif path == '/ABC':
        #     start_response('200 OK', [('Content-Type', 'text/html')])
        #     return [f'Page -  {path}'.encode('utf-8')]
        #
        # else:
        #     start_response('ERROR 404', [('Content-Type', 'text/html')])
        #     return [b'path is not recognized']

# application = Application(routes, fronts)
