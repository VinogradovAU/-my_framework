# page controller
# def index_view(request):
#     print(request)
#     return '200 OK', [b'index_view']
#
#
# def contacts_view(request):
#     print(request)
#     return '200 OK', [b'contacts_view']
#
#
# def services_view(request):
#     print(request)
#     return '200 OK', [b'services_view']
#
#
# def error_404_view(request):
#     print(request)
#     return '404 ERROR', [b'error_404_view']
#
#
# class Other:
#     def __call__(self, request):
#         print(request)
#         return '200 OK', [b'<h1>other_view</h1>']
#
#
# routes = {
#     '/': index_view,
#     '/contacts/': contacts_view,
#     '/services/': services_view,
#     '/other/': Other()
# }
#
#
# # Front controllers
#
# def secret_front(request):
#     request['secret'] = 'some secret'
#
#
# def other_front(request):
#     request['other_key'] = 'key'
#
#
# fronts = [secret_front, other_front]


# функция исправляем проблемы кодировки кирилических символов
import quopri

import views


def decode_value(val):
    val_b = bytes(val.replace('%', '=').replace("+", " "), 'UTF-8')
    val_decode_str = quopri.decodestring(val_b)
    return val_decode_str.decode('UTF-8')


class Application():
    def __init__(self, routes: dict, fronts: list):
        self.routes = routes
        self.fronts = fronts

    def parse_input_data(self, data):
        result = {}
        if data:
            # делим параметры через &
            params = data.split('&')
            for item in params:
                # делим ключ и значение через =
                k, v = item.split('=')
                result[k] = v
        return result

    # функция читаем байны - POST из запроса
    def get_wsgi_input_data(self, environ):
        # получаем длину тела
        content_length_data = environ.get('CONTENT_LENGTH')
        # приводим к int
        content_length = int(content_length_data) if content_length_data else 0
        # считываем данные если они есть
        data = environ['wsgi.input'].read(content_length) if content_length > 0 else b''
        return data

    # функция получает байты на вход, декодирует и возвращает словарь
    def parse_wsgi_input_data(self, data):
        result = {}
        if data:
            # декодируем данные
            data_str = data.decode(encoding='utf-8')
            # собираем их в словарь
            result = self.parse_input_data(data_str)
        return result

    def __call__(self, environ, start_response):
        # print(environ)
        # print(type(environ))
        print('work')

        # Метод которым отправили запрос
        method = environ['REQUEST_METHOD']
        # print('method', method)
        # обработка GET запроса. если был GET то вернется словарь
        # получаем параметры запроса
        get_query = environ['QUERY_STRING']
        # print(get_query)
        # превращаем параметры в словарь
        get_params = self.parse_input_data(get_query)

        # get POST request
        get_post_bytes = self.get_wsgi_input_data(environ=environ)

        # get dict from POST bytes
        get_post_dict = self.parse_wsgi_input_data(get_post_bytes)

        path = environ['PATH_INFO']
        if len(path) > 1:
            if path[-1:] != '/':
                path = path + '/'

        if path in self.routes:
            # print(f'-----------> {self.routes[path]}')
            view = self.routes[path]
        else:
            view = views.error_404_view

        request = {}
        # добавим GET параметры в request
        if get_params:
            print('-' * 100)
            print(f'Приняты GET данные:')
            print(get_params)
            request['get_params'] = get_params
            print('-' * 100)

        # добавим POST параметры в request
        if get_post_dict:
            request['post_params'] = get_post_dict
            print('-'*100)
            print(f'POST data: {get_post_dict}')
            print('-' * 100)
            print(f'Приняты POST данные:')
            for k in get_post_dict:
                print(decode_value(get_post_dict[k]))
            print('-' * 100)

        for front in self.fronts:
            front(request)

        code, body = view(request)
        start_response(code, [('Content-Type', 'text/html')])

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
