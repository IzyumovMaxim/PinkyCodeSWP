import os
import requests
from urllib.parse import urljoin

BASE_URL = "https://pinkycode.mooo.com/?login=1"  # Замените на URL вашего сервера

def test_user_login():
    # Данные для входа
    login_data = {
        'email': 'admin@mail.ru',
        'password': 'admin'
    }

    # Отправляем POST-запрос для входа
    response = requests.post(urljoin(BASE_URL, "/"), data=login_data)

    # Проверяем, что ответ успешный (статус 200)
    print(response.content)
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"

    # Проверяем, что сессия создана (cookie session_id существует)
    cookies = response.cookies
    assert 'session_id' in cookies, "Session cookie not found"

    # Проверяем, что пользователь перенаправлен на index.html
    assert b"Upload" in response.content, "User was not redirected to index.html"

def test_non_existing_user_login():
    # Данные для входа
    login_data = {
        'email': 'some@mail.ru',
        'password': '123'
    }

    # Отправляем POST-запрос для входа
    response = requests.post(urljoin(BASE_URL, "/"), data=login_data)
    assert b"Login" in response.content, "User was redirected to other page"