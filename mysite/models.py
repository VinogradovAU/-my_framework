from reusepatterns.prototypes import PrototypeMixin
from logging_mod import Logger

logger = Logger('model')

# абстрактный пользователь
class User:
    pass


# преподаватель
class Teacher(User):
    pass


# студент
class Student(User):
    pass


# Фабрика пользователей
class UserFactory:
    types = {
        'student': Student,
        'teacher': Teacher
    }

    @classmethod
    def create(cls, type_):
        return cls.types[type_]()


# Категория
class Category:
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


# Курс
class Course(PrototypeMixin):

    def __init__(self, name, category):
        self.name = name
        self.category = category
        self.category.courses.append(self)


# Интерактивный курс
class InteractiveCourse(Course):
    pass


# Курс в записи
class OfflineCourse(Course):
    pass


# Фабрика курсов
class CourseFactory:
    types = {
        'interactive': InteractiveCourse,
        'OfflineCourse': OfflineCourse
    }

    @classmethod
    def create(cls, type_, name, category):
        return cls.types[type_](name, category)


# Основной класс - интерфейс проекта
class TrainingSite:
    def __init__(self):
        self.teachers = []
        self.students = []
        self.courses = []
        self.categories = []

    @staticmethod
    def create_user(type_):
        return UserFactory.create(type_)

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
    def create_course(type_, name, category):
        return CourseFactory.create(type_, name, category)

    def get_course(self, name) -> Course:
        for item in self.courses:
            logger.log(f'найден объект курса {item} с именем {item.name}')
            if item.name == name:
                return item
        return None
