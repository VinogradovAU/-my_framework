try:
    from templator import render
    import datetime
except Exception as e:
    print(f'Error import module {e}')
    exit(1)


# page controller
def index_view(request):
    secret = request.get('secret', None)
    urls = request.get('urls', None)
    # Используем шаблонизатор
    return '200 OK', [render('index.html', secret=secret, urls=urls)]


def contacts_view(request):
    value = request.get('value', None)
    urls = request.get('urls', None)
    # Используем шаблонизатор
    return '200 OK', [render('contacts.html', value=value, urls=urls)]


def services_view(request):
    urls = request.get('urls', None)
    return '200 OK', [render('contacts.html', value=services_view, urls=urls)]



class Other:
    def __call__(self, request):
        urls = request.get('urls', None)
        html = '<h1>Menu</h1>'
        for item in urls:
            html = html + f'<li><a href="{item}">{item}</a></li>'

        return '200 OK', [html.encode('utf-8')]


def error_404_view(request):
    print(request)
    return '404 ERROR', [b'<h1>error_404_view</h1>']
