import json
import time
import tldextract

import redis
from django.http import (
    HttpResponseNotFound,
    HttpResponseBadRequest,
    JsonResponse,
)
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.conf import settings
from rest_framework.response import Response


# connect to our Redis instance
redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,
                                   port=settings.REDIS_PORT, db=0)


def clearing_links(links):
    '''
    С помощью этой функции мы выделяем домен ссылок.
    Далее сохроняем только уникальные ссылки в списке.
    '''
    clean_links = []
    for index in range(len(links)):
        link = links[index]
        extracted = tldextract.extract(link)
        s = '{}.{}'.format(extracted.domain, extracted.suffix)
        domain_parts = s.split('.')
        if domain_parts[-1].isalpha():
            clean_links.append(s)
    unique_links = list(set(clean_links))
    return unique_links


@csrf_exempt
def save_visited_links(request):
    '''
    Функция сохранения в БД Redis переданного списка доменов и времени
        обращения к ним.
    '''
    error_content = 'The list must contain the "name.domain"!'
    if request.method == 'POST':
        try:
            content = json.loads(request.body)
            clean_links = clearing_links(content['links'])
            if clean_links:
                record_time = round(time.time())
                redis_instance.sadd(record_time, *clean_links)
                return JsonResponse(data={'status': 'ok'}, status=201)
        except KeyError:
            error_content = 'The key should be name "links"!'
        except Exception as e:
            error_content = e
        return HttpResponseBadRequest(content=error_content)
    return HttpResponseNotFound('Only the "POST" method works!')


@csrf_exempt
def get_visited(request):
    '''
    Функция получения списка уникальных посещенных доменов за переданный
        интервал времени
    '''
    if request.method == 'GET':
        try:
            start_time = int(request.GET.get('from'))
            end_time = int(request.GET.get('to')) + 1
            links = set()
            for record_time in range(start_time, end_time):
                if redis_instance.smembers(str(record_time)):
                    links.update(redis_instance.smembers(str(record_time)))
            domains = [link.decode('utf-8') for link in links]
            return JsonResponse(
                data={'domains': domains, 'status': 'ok'
                      },
                status=200,
            )
        except Exception as e:
            return HttpResponseBadRequest(content=e)
    return HttpResponseNotFound()


@api_view(['GET'])
def manage_items(request):
    '''
    Функция выводит все записи БД.
    ключ/значение-время записи ссылок/уникальные домены ссылок.
    '''
    if request.method == 'GET':
        items = {}
        count = 0
        for key in redis_instance.keys('*'):
            items[key.decode("utf-8")] = redis_instance.smembers(key)
            count += 1
        response = {
            'count': count,
            'msg': f"Found {count} items.",
            'items': items
        }
        return Response(response, status=200)
