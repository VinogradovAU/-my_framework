from reusepatterns.singletones import SingletonByName
import time
import sys
import os.path

# Заметка, можно применить стратегию если добавить стратегию логирования
class Logger(metaclass=SingletonByName):

    def __init__(self, name):
        self.name = name

    def log(self, text):
        with open('./logs/log.log', 'a', encoding='utf-8') as fd:
            fd.seek(0, 2)
            fd.write(f'\n + {time.asctime()} [{self.name}] + {text}')


# декоратор
def debug(func):
    def inner(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        # время выплнения функции выводим в консоль
        print('DEBUG-------->', func.__name__, end - start)
        return result

    return inner

if __name__ == '__main__':
    LOG = Logger('logger')

    LOG.log('Тестовая запись №1')
    LOG.log('Тестовая запись №2')
    LOG.log('Тестовая запись №3')
    LOG.log('Тестовая запись №4')
