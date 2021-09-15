# WEB-приложение для учета посещенных ссылок
Приложение предоставляет три эндпойнта:

POST /visited_links для загрузки посещений.

GET /visited_domains?from=1545221231&to=1545217638 для получения статистики.

GET /all_visited для получения времени всех посещеных уникальных доменов.

• Первый ресурс служит для передачи в сервис массива ссылок в POST-запросе. Временем их посещения считается время получения запроса сервисом.

Запрос
```
POST /visited_links

{
"links": [
"https://ya.ru",
"https://ya.ru?q=123",
"funbox.ru",
"https://stackoverflow.com/questions/11828270/how-to-exit-the-vim-editor"
]
}
```
Ответ
```
{
"status": "ok"
}
```
• Второй ресурс служит для получения GET-запросом списка уникальных доменов,
посещенных за переданный интервал времени.

Запрос
```
GET /visited_domains?from=1545221231&to=1545217638
```
Ответ 
```
{
"domains": [
"ya.ru",
"funbox.ru",
"stackoverflow.com"
],
"status": "ok"
}
```
• Поле status ответа служит для передачи любых возникающих при обработке запроса
ошибок.

• Для хранения данных сервис  использует БД Redis.

• Третий эндпойнт служит для получения времени всех посещеных уникальных доменов.


## Стек

Python 3, Django 3.2, Django REST Framework, GIT, Redis


## Установка 
Клонируем репозиторий на локальную машину:

```git clone https://github.com/Basil2587/tracking_visited.git```

В директории проекта создайте файл .env: 
  - SECRET_KEY=можно сгенерировать [по адресу](https://djecrety.ir)

Создаем виртуальное окружение:  ```python3 -m venv venv```

Активировать виртуальное окружение (для Linux): ```source venv/bin/activate```

Устанавливаем зависимости: ```pip install -r requirements.txt```

Запускаем django сервер: ```python manage.py runserver```

## Тестирование

Запустить PyTest командой: ```pytest```