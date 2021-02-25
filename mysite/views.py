try:
    from templator import render
    import datetime
except Exception as e:
    print(f'Error import module {e}')
    exit(1)

from logging_mod import Logger
from models import TrainingSite

logger = Logger('views')
site = TrainingSite()


# page controller
def index_view(request):
    secret = request.get('secret', None)
    urls = request.get('urls', None)
    get_params = request.get('get_params', None)
    css_url = request.get('css_url', None)
    logger.log('----> Отработал index_view')
    # Используем шаблонизатор
    return '200 OK', [render('index.html',
                             secret=secret,
                             urls=urls,
                             get_params=get_params, css_url=css_url)]


def contacts_view(request):
    value = request.get('value', None)
    urls = request.get('urls', None)
    get_params = request.get('get_params', None)
    # Используем шаблонизатор
    return '200 OK', [render('contacts.html',
                             value=value,
                             urls=urls,
                             get_params=get_params)]


def categories_view(request):
    urls = request.get('urls', None)
    return '200 OK', [render('categories.html',
                             value="categories_view",
                             urls=urls,
                             categories=site.categories)]


def css_view(request):
    print(f'i am in css_view')
    return '222 OK', [render('style.css', folder='./static/')]


class Courses:
    def __call__(self, request):
        urls = request.get('urls', None)
        get_params = request.get('get_params', None)

        return '200 OK', [render('courses.html',
                                 value="courses_view",
                                 urls=urls,
                                 categories=site.categories)]


def create_course(request):
    urls = request.get('urls', None)
    print(f'я в create_course view')
    try:
        if request['post_params']:
            print(f'request["post_params"]--->{request["post_params"]}')
            cat_id = request['post_params']['category_id']
            print(f'cat_id = {cat_id}')
            cat_obj = site.find_category_by_id(int(cat_id))
            print(f'cat_obj type = {type(cat_obj)}, {cat_obj.name}')

            type_of_course = 'interactive'
            if request["post_params"]['on_off_line']:
                type_of_course = 'OfflineCourse'
            site.create_course(type_of_course, request['post_params']['name'], cat_obj)

            logger.log(f"В категорию {cat_obj.name} добавлен курс {request['post_params']['name']}")
            return '200 OK', [render('create_course.html',
                                     value=f"В категорию {cat_obj.name} добавлен курс {request['post_params']['name']}",
                                     urls=urls,
                                     categories=site.categories, )]
    except Exception as e:
        pass

    return '200 OK', [render('create_course.html',
                             value="create_course",
                             urls=urls,
                             categories=site.categories,)]


def create_category(request):
    urls = request.get('urls', None)
    try:
        if request['post_params']:
            post_data = request['post_params']
            new_category = post_data['name']
            # проверить есть ли уже такая категория
            for item in site.categories:
                print(f'идем по категориям . ищем совпадение с новой')
                if item.name == new_category:
                    logger.log(f'Категория уже существует')
                    return '200 OK', [render('create_category.html',
                                             value="Категория уже существует. Введите другое название!",
                                             urls=urls,
                                             categories=site.categories)]
            # если нет, то создать новую
            print(f'Создаем новую категорию')
            # category = None
            # if category_id:
            #     category = site.find_category_by_id(int(category_id))

            new_category_obj = site.create_category(new_category)
            site.categories.append(new_category_obj)
            logger.log(f'site.categories--->{site.categories}')

            logger.log(f'получены POST данные: {post_data}')
    except Exception as e:
        pass
    return '200 OK', [render('create_category.html',
                             value="create_category",
                             urls=urls,
                             categories=site.categories)]


def copy_course(request):
    urls = request.get('urls', None)
    return '200 OK', [render('copy_course.html',
                             value="copy_course",
                             urls=urls)]


def error_404_view(request):
    print(request)
    return '404 ERROR', [b'<h1>error_404_view</h1>']
