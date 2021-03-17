try:
    from templator import render
    import datetime

except Exception as e:
    print(f'Error import module {e}')
    exit(1)

import logging_mod

from models import TrainingSite, EmailNotifier, SmsNotifier, BaseSerializer
from cbv_classes import ListView, CreateView
from my_orm import UnitOfWork, DomainObject
from mappers import MapperRegistry

logger = logging_mod.Logger('views')
site = TrainingSite()

# загружаем списки объектами из БД (если происходит перезагрузка сайта/скрипта)
if not site.students:
    result = MapperRegistry.get_current_mapper('student').all()
    site.students = result
    for k in site.students:
        print(f'name:{k.name} -----> id: {k.id}')

if not site.courses:
    result = MapperRegistry.get_current_mapper('course').all()
    site.courses = result

if not site.categories:
    result = MapperRegistry.get_current_mapper('category').all()
    site.categories = result


email_notifier = EmailNotifier()
sms_notifier = SmsNotifier()
urlpatterns = {}

UnitOfWork.new_current()
UnitOfWork.get_current().set_mapper_registry(MapperRegistry)


def add_route(url):
    # паттерн-декоратор
    def inner(view):
        urlpatterns[url] = view

    return inner


# page controller
@add_route('/')
@logging_mod.debug
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


@logging_mod.debug
@add_route('/contacts/')
def contacts_view(request):
    value = request.get('value', None)
    urls = request.get('urls', None)
    get_params = request.get('get_params', None)
    # Используем шаблонизатор
    return '200 OK', [render('contacts.html',
                             value=value,
                             urls=urls,
                             get_params=get_params)]


'''
@logging_mod.debug
@add_route('/categories/')
def categories_view(request):
    urls = request.get('urls', None)
    return '200 OK', [render('categories.html',
                             value="categories_view",
                             urls=urls,
                             categories=site.categories)]
'''


@add_route('/style.css/')
@logging_mod.debug
def css_view(request):
    # print(f'i am in css_view')
    return '222 OK', [render('style.css', folder='./static/')]


@add_route('/deb/')
def debug_view(request):
    urls = request.get('urls', None)
    print(f'site.students--->{site.students}')
    for k in site.students:
        print(k.courses)
    print(f'site.courses--->{site.courses}')
    print(f'site.categories--->{site.categories}')
    return '200 OK', [render('deb.html',
                             urls=urls,
                             students=site.students,
                             courses=site.courses,
                             categories=site.categories)]


class Courses:
    def __call__(self, request):
        urls = request.get('urls', None)
        get_params = request.get('get_params', None)
        mapper = MapperRegistry.get_current_mapper('course')
        cou = mapper.all()
        type_of_course = 'interactive'
        # проверяю есть ли объекты курсов в списке site.course
        if site.courses:
            for item in cou:
                in_list = False
                for el in site.courses:
                    if item.name == el.name and item.category_id == el.category_id:
                        in_list = True
                if not in_list:
                    # не нашли в списке. надо создать объект и положить в список
                    course = site.create_course(type_of_course, item.name, item.category_id)
                    site.courses.append(course)

        else:
            # создаем объекты курсов и загружаем их в список
            for item in cou:
                course = site.create_course(type_of_course, item.name, item.category_id)
                site.courses.append(course)

        cats_all = MapperRegistry.get_current_mapper('category').all()
        cats_dict = {}
        for k in cats_all:
            cats_dict[k.id - 1] = k.name

        print(f'cats_dict---->{cats_dict}')
        return '200 OK', [render('courses.html',
                                 value="courses_view",
                                 urls=urls,
                                 cats_dict=cats_dict,
                                 courses=cou)]


@add_route('/create_course/')
def create_course(request):
    urls = request.get('urls', None)
    print(f'я в create_course view')
    try:
        if request['post_params']:
            # print(f'request["post_params"]--->{request["post_params"]}')
            cat_id = request['post_params']['category_id']
            # print(f'cat_id = {cat_id}')
            cat_obj = site.find_category_by_id(int(cat_id))
            # print(f'cat_obj type = {type(cat_obj)}, {cat_obj.name}')

            type_of_course = 'interactive'
            if request["post_params"]['on_off_line']:
                type_of_course = 'OfflineCourse'
            course = site.create_course(type_of_course, request['post_params']['name'], cat_obj.id)
            course.observers.append(email_notifier)
            course.observers.append(sms_notifier)
            site.courses.append(course)

            # создаем новую запись о курсе в БД (имя и id категории)
            course.mark_new()
            UnitOfWork.get_current().commit()

            # получаем id курса из БД, чтобы вписать его в объект класса находящийся в списке site.courses
            curs_id = MapperRegistry.get_current_mapper('course').find_by_name(course.name)
            course_obj = site.get_course(course.name)
            course_obj.id = curs_id

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
                             categories=site.categories, )]


@add_route('/create_category/')
def create_category(request):
    urls = request.get('urls', None)
    try:
        if request['post_params']:
            post_data = request['post_params']
            new_category = post_data['name']
            # проверить есть ли уже такая категория
            for item in site.categories:
                # print(f'идем по категориям . ищем совпадение с новой')
                if item.name == new_category:
                    logger.log(f'Категория уже существует')
                    return '200 OK', [render('create_category.html',
                                             value="Категория уже существует. Введите другое название!",
                                             urls=urls,
                                             categories=site.categories)]
            # если нет, то создать новую
            # print(f'Создаем новую категорию')
            # category = None
            # if category_id:
            #     category = site.find_category_by_id(int(category_id))

            new_category_obj = site.create_category(new_category)
            site.categories.append(new_category_obj)
            new_category_obj.mark_new()
            UnitOfWork.get_current().commit()
            logger.log(f'site.categories--->{site.categories}')

            logger.log(f'получены POST данные: {post_data}')
    except Exception as e:
        pass
    return '200 OK', [render('create_category.html',
                             value="create_category",
                             urls=urls,
                             categories=site.categories)]


@add_route('/copy-course/')
def copy_course(request):
    logger.log(f'Внутри copy_course')
    urls = request.get('urls', None)
    print(f'request------>{request}')
    if request['post_params']:
        post_data = request['post_params']
        old_course = post_data['name']
        logger.log(f'Ищем курс с именем --> {old_course}')
        source_course_obj = site.get_course(old_course)
        logger.log(f'Поиск вернул объект --> {source_course_obj}')

        # формируем список категорий длоя вывода на страницу
        cats_all = MapperRegistry.get_current_mapper('category').all()
        cats_dict = {}
        for k in cats_all:
            cats_dict[k.id - 1] = k.name

        if source_course_obj:
            new_name = f'copy_{old_course}'
            new_course = source_course_obj.clone()
            new_course.name = new_name

            new_course.mark_new()
            UnitOfWork.get_current().commit()
            print(new_course.__dict__)
            site.courses.append(new_course)
            logger.log(f'создана копия курса --> {new_course}')
            return '200 OK', [render('courses.html',
                                     value="courses_view",
                                     urls=urls,
                                     cats_dict=cats_dict,
                                     courses=site.courses)]
        else:
            logger.log(f'Не удалось создать копию курса {old_course}')
            return '200 OK', [render('courses.html',
                                     value="courses_view",
                                     urls=urls,
                                     cats_dict=cats_dict,
                                     courses=site.courses)]
    else:
        error_404_view(request)


'''

@add_route('/student-list/')
def student_list(request):
    urls = request.get('urls', None)
    return '200 OK', [render('student_list.html',
                             value="student-list",
                             students=site.students)]
'''


@add_route('/create-student/')
def create_student(request):
    urls = request.get('urls', None)
    if 'post_params' in request and 'name' in request["post_params"]:
        # print(f'request["post_params"]--->{request["post_params"]}')
        name_student = request['post_params']['name']
        # print(f'{name_student}')

        for k in site.students:
            if k.name == name_student:
                logger.log(f'Студент с именем {name_student} уже зарегистрирован')
                return '200 OK', [render('create_student.html',
                                         value="create-student_view",
                                         info_text=f'Студент с именем {name_student} уже зарегистрирован')]
        stud_obj = site.create_user(type_='student', name=name_student)
        site.students.append(stud_obj)
        stud_obj.mark_new()
        UnitOfWork.get_current().commit()
        logger.log(f'Студент с именем {name_student} зарегистрирован в системе')
        return '200 OK', [render('create_student.html',
                                 value="create-student_view",
                                 info_text=f'Студент с именем {name_student} зарегистрирован в системе')]
    #     else:
    #         return '200 OK', [render('create_student.html',
    #                                  value="create-student_view")]
    # except Exception as e:
    #     print(f'Ошибка создания объекта студента {e}')
    #     return '200 OK', [render('create_student.html', value="create-student_view")]

    return '200 OK', [render('create_student.html',
                             value="create-student_view")]


@add_route('/add-student/')
def add_student(request):
    urls = request.get('urls', None)
    # if not site.students:
    #     result = MapperRegistry.get_current_mapper('student').all()
    #     site.students = result
    # if not site.courses:
    #     result = MapperRegistry.get_current_mapper('course').all()
    #     site.courses = result

    if 'post_params' in request and 'course_name' in request["post_params"] and 'student_name' in request[
        "post_params"]:
        # print(f'request["post_params"]--->{request["post_params"]}')
        name_student = request['post_params']['student_name']
        course_name = request['post_params']['course_name']
        student_obj = site.get_student(name_student)
        course_obj = site.get_course(course_name)
        student_id_from_db = MapperRegistry.get_current_mapper('student').find_by_name(name_student)
        course_id_from_db = MapperRegistry.get_current_mapper('course').find_by_name(course_name)

        # записывам данные в БД (id курса, id студента)
        MapperRegistry.get_current_mapper('student').add_course(course_id_from_db, student_obj.id)

        if student_obj and course_obj:
            course_obj.add_student(student_obj)
            return '200 OK', [render('add_student.html',
                                     info_text=f'Студент {student_obj.name} добавлен на курс {course_obj.name}',
                                     courses=site.courses,
                                     students=site.students)]


    return '200 OK', [render('add_student.html',
                             info_text="add-student_view",
                             courses=site.courses,
                             students=site.students)]


def error_404_view(request):
    # print(request)
    return '404 ERROR', [b'<h1>error_404_view</h1>']


@add_route('/api/')
def course_api(request):
    # logger.log(f'Метод view course_api передаю {site.courses}')
    ret = BaseSerializer(site.courses).save()
    # print(f'type()-->{type(ret)}')
    logger.log(f'Отправка данных /api/ --->{ret}')
    print(f'Отправка данных /api/ --->{ret}')
    return '200 OK', [ret.encode('utf-8')]


class CategoryListView(ListView):
    queryset = site.categories
    template_name = 'categories.html'

    def get_queryset(self):
        mapper = MapperRegistry.get_current_mapper('category')
        return mapper.all()


class StudentListView(ListView):
    queryset = site.students
    template_name = 'student_list.html'

    def get_queryset(self):
        mapper = MapperRegistry.get_current_mapper('student')
        return mapper.all()

    def get_context_data(self):
        queryset = self.get_queryset()
        context_object_name = super().get_context_object_name()
        logger.log(f'context_object_name = {context_object_name}')
        for el in queryset:
            course_ids = MapperRegistry.get_current_mapper('student').get_courses(el.id)
            for k in course_ids:
                for course in site.courses:
                    if course.category_id == k[0]-1:
                        el.courses.append(course)

        context = {context_object_name: queryset}
        return context
