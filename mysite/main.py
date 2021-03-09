from wsgiref.simple_server import make_server


import datetime
import sys
import os
from logging_mod import Logger
import urls
logger = Logger('main')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, 'framework'))
print(sys.path)


try:

    from engin import Application, DebugApplication, FakeApplication
    import views
except Exception as e:
    print(f'Error import module {e}')
    exit(1)




# Front Controller
def secret_front(request):
    request['secret'] = 'some secret'
    request['value'] = datetime.datetime.now()  # значение даты для вывода в копирайт
    # logger.log('----> Отработал secret_front')


def urls_list_front(request):
    request['urls'] = list(urls.urlpatterns.keys())


def css_list_front(request):
    request['css_list'] = "/style.css"



front_controllers = [
    secret_front,
    urls_list_front,
    css_list_front,
]

# ОСНОВНОЙ ЗАПУСК
application = Application(urls.urlpatterns, front_controllers)


# альтернативный запуск приложения
# application = DebugApplication(urls.urlpatterns, front_controllers)

# application = FakeApplication(urls.urlpatterns, front_controllers)


with make_server('', 8000, application) as httpd:
    print("Serving HTTP on port 8000...")

    # Respond to requests until process is killed
    httpd.serve_forever()
