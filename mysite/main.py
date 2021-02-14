import datetime
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, 'framework'))
print(sys.path)

try:

    from engin import Application
    import views
except Exception as e:
    print(f'Error import module {e}')
    exit(1)

urlpatterns = {
    '/': views.index_view,
    '/contacts/': views.contacts_view,
    '/services/': views.services_view,
    '/other/': views.Other()
}


# Front Controller
def secret_front(request):
    request['secret'] = 'some secret'
    request['value'] = datetime.datetime.now()  # значение даты для вывода в копирайт

def urls_list_front(request):
    request['urls'] = list(urlpatterns.keys())

front_controllers = [
    secret_front,
    urls_list_front
]

application = Application(urlpatterns, front_controllers)