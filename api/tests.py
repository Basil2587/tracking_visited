import time

import pytest
from api.views import clearing_links

POST_URL = '/visited_links'
GET_URL = '/visited_domains'
json_input = {
    "links": [
        "https://ya.ru",
        "https://ya.ru?q=123",
        "funbox.ru",
        "https://stackoverflow.com/questions/11828270//how-to-exit-the-vim"
        "-editor",
        "www.fun.com",
        "http://samo.tk"
        ],
    }


def test_links_url():
    # Проверка на получении списка уникальных доменов
    list_links = list(json_input.values())[0]
    clean_domains = [
        'fun.com', 'stackoverflow.com', 'ya.ru', 'samo.tk', 'funbox.ru']
    assert sorted(clearing_links(list_links)) == sorted(clean_domains)

    not_links = ['ya.', '.ya', 'ya', 'y.a']
    assert clearing_links(not_links) == []


def test_wrong_methods(client):
    response = client.get(POST_URL)
    assert response.status_code == 404
    response = client.post(GET_URL)
    assert response.status_code == 404


def test_post_check_errors(client):
    # Проверка пост-метода на ошибки
    json_er_input = [
        {'linksg': ['sd.com']},  # неправельно указан ключ "links"
        None,  # пусто
        {},  # пустой json
        {'links': ['sf']},  # неправильная ссылка
        {'links': []}  # пустое значение
        ]
    for data in json_er_input:
        response = client.post(POST_URL, data, content_type='application/json')
        assert response.status_code == 400


def test_add_links(client):
    # Проверка сохранения ссылок

    json_output = {'status': 'ok'}
    response = client.post(POST_URL, json_input,
                           content_type='application/json')
    assert response.status_code == 201
    assert response.json() == json_output


def test_get(client):
    # Проверка работы Get запроса

    json_output = {'domains': [], 'status': 'ok'}
    response = client.get(GET_URL + '?from=0&to=1',
                          content_type='application/json')
    assert response.status_code == 200
    assert response.json() == json_output


@pytest.mark.parametrize('start, end', [
    (None, None), ('1', None), (None, '1'), ('11', ''), ('a', 's')])
def test_check_errors(client, start, end):
    # Проверка Get запроса на ошибки, на некорректность указанного времени
    response = client.get(
        GET_URL + '?from={0}&to={1}'.format(start, end),
        content_type='application/json',
    )
    assert response.status_code == 400


def test_post_get(client):
    # Проверяем, что записанные ссылки находятся в переданном интервале времени
    now_time = round(time.time())
    response = client.post(POST_URL, json_input,
                           content_type='application/json')
    assert response.status_code == 201

    response = client.get(
        GET_URL + '?from={}&to={}'.format(now_time, now_time+1),
        content_type='application/json',
    )
    assert response.status_code == 200
    domains = response.json()['domains']
    assert 'ya.ru' in domains
    assert 'funbox.ru' in domains
    assert 'stackoverflow.com' in domains
    assert 'fun.com' in domains
    assert 'samo.tk' in domains
    assert domains.count('ya.ru') == 1

    response = client.get(
        GET_URL + '?from={}&to={}'.format(now_time + 2, now_time + 100),
        content_type='application/json',
    )
    assert response.status_code == 200
    domains = response.json()['domains']
    assert 'ya.ru' not in domains
    assert 'funbox.ru' not in domains
    assert 'stackoverflow.com' not in domains
    assert 'fun.com' not in domains
    assert 'samo.tk' not in domains
