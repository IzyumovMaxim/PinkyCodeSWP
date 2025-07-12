import unittest
import os
import sys

from .pinky_test_version import application

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

environ = {
    # Информация о сервере и окружении
    "REQUEST_METHOD": "POST",                    # HTTP-метод (GET, POST, PUT и т.д.)
    "PATH_INFO": "/submit",                     # Путь запроса (например, /index.html)
    "QUERY_STRING": "file=file.notzip",         # Строка запроса (параметры GET)
    "CONTENT_TYPE": "application/x-www-form-urlencoded",  # Тип содержимого тела запроса
    "CONTENT_LENGTH": "16",                     # Размер тела запроса в байтах
    "SERVER_NAME": "localhost",                 # Имя сервера
    "SERVER_PORT": "8080",                      # Порт сервера
    "SERVER_PROTOCOL": "HTTP/1.1",              # Версия протокола HTTP
    "wsgi.version": (1, 0),                     # Версия WSGI
    "wsgi.url_scheme": "http",                  # Схема URL (http или https)
    "wsgi.input": open(f"{os.path.dirname(os.path.abspath(__file__))}/codetest.txt", "rb"), # Входной поток данных (тело запроса)
    "wsgi.errors": ...,                         # Поток для записи ошибок
    "wsgi.multithread": True,                   # Поддерживает ли сервер многопоточность
    "wsgi.multiprocess": False,                 # Поддерживает ли сервер многопроцессность
    "wsgi.run_once": False,                     # Запускается ли приложение один раз

    # Заголовки HTTP (преобразованы в переменные окружения)
    "HTTP_HOST": "localhost:8080",              # Заголовок Host
    "HTTP_USER_AGENT": "Mozilla/5.0",           # Заголовок User-Agent
    "HTTP_ACCEPT": "text/html",                 # Заголовок Accept
    "HTTP_CONTENT_TYPE": "application/x-www-form-urlencoded",  # Заголовок Content-Type
    "HTTP_CONTENT_LENGTH": "27",                # Заголовок Content-Length
}

class TestNotZipUpload(unittest.TestCase):
    def setUp(self):
        self.app = application
        self.environ = environ
        self.start_response = (lambda error, headers: ...)

    def test_not_zip_upload(self):
        self.assertEqual(self.app(self.environ, self.start_response), [b"Send a file\n"])