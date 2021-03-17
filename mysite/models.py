import os
import sys

from reusepatterns.prototypes import PrototypeMixin
from reusepatterns.observer import Subject, Observer
import jsonpickle

from my_orm.unitofwork import DomainObject
from logging_mod import Logger

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, 'my_orm'))

logger = Logger('model')


# абстрактный пользователь
class User:
    def __init__(self, name):
        self.name = name


# преподаватель
class Teacher(User):
    pass


# студент
class Student(User, DomainObject):
    id = None

    def __init__(self, name):
        self.courses = []
        logger.log(f'я в __init__ класса Student перед super().__init__({name})')
        super().__init__(name)


# Фабрика пользователей
class UserFactory:
    types = {
        'student': Student,
        'teacher': Teacher
    }

    @classmethod
    def create(cls, type_, name):
        logger.log(f'я в методе create UserFactory c типом {type_}')
        return cls.types[type_](name)


# Категория
class Category(DomainObject):
    # реестр?
    auto_id = 0

    def __init__(self, name, category):
        self.id = Category.auto_id
        Category.auto_id += 1
        self.name = name
        self.category = category
        self.courses = []

    def course_count(self):
        result = len(self.courses)
        if self.category:
            result += self.category.course_count()
        return result


class Course(PrototypeMixin, Subject, DomainObject):

    def __init__(self, name, category_id):
        self.id = id
        self.name = name
        self.category_id = category_id
        self.students = []
        super().__init__()

    def add_student(self, student: Student):
        self.students.append(student)
        student.courses.append(self)
        logger.log(f'add_student перед notify')
        self.notify()


# Курс
# class Course(PrototypeMixin, Subject, DomainObject):
#     # реестр
#     auto_id = 0
#
#     def __init__(self, name, category):
#         self.id = Course.auto_id
#         Course.auto_id += 1
#         self.name = name
#         self.category = category
#         self.category.courses.append(self)
#         self.students = []
#         super().__init__()
#
#     def __getitem__(self, item):
#         return self.students[item]
#
#     def add_student(self, student: Student):
#         self.students.append(student)
#         student.courses.append(self)
#         logger.log(f'add_student перед notify')
#         self.notify()

class SmsNotifier(Observer):

    def update(self, subject: Course):
        print('SMS->', 'к нам присоединился', subject.students[-1].name)


class EmailNotifier(Observer):

    def update(self, subject: Course):
        print(('EMAIL->', 'к нам присоединился', subject.students[-1].name))


class BaseSerializer:

    def __init__(self, obj):
        self.obj = obj

    def save(self):
        return jsonpickle.dumps(self.obj)

    def load(self, data):
        return jsonpickle.loads(data)


# Интерактивный курс
class InteractiveCourse(Course):
    pass


# Курс в записи
class OfflineCourse(Course):
    pass


class StudentCourse(DomainObject):

    def __init__(self, student, course):
        self.student_id = student.id
        self.course_id = course.id


# Фабрика курсов
class CourseFactory:
    types = {
        'interactive': InteractiveCourse,
        'OfflineCourse': OfflineCourse
    }

    @classmethod
    def create(cls, type_, name, category_id):
        return cls.types[type_](name, category_id)


# Основной класс - интерфейс проекта
class TrainingSite:
    def __init__(self):
        self.teachers = []
        self.students = []
        self.courses = []
        self.categories = []


    @staticmethod
    def create_user(type_, name):
        return UserFactory.create(type_, name)

    @staticmethod
    def create_category(name, category=None):
        logger.log(f'Создаем новый объект категории {name}')
        return Category(name, category)

    def find_category_by_id(self, id):
        for item in self.categories:
            if item.id == id:
                print('Возвращяю объект категории с id = ', item.id)
                return item
        raise Exception(f'Нет категории с id = {id}')

    @staticmethod
    def create_course(type_, name, category_id):
        return CourseFactory.create(type_, name, category_id)

    def get_course(self, name) -> Course:
        for item in self.courses:
            logger.log(f'найден объект курса {item} с именем {item.name}')
            if item.name == name:
                return item
        return None

    def get_student(self, name) -> Student:
        for item in self.students:
            logger.log(f'найден объект студент {item} с именем {item.name}')
            if item.name == name:
                return item
