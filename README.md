# Тестовое задание
## Задание 
Напишите RESTful API сервис на Python, который будет предоставлять CRUD операции для работы с базой данных, содержащей информацию о пользователях.

### Описание 
## Использованные технологии

- Python
- FastAPI
- Docker
- docker compose
- SQLite
- SQLAlchemy
- Fastapi-Users  JWT

### Инструкция по развертыванию проекта.

1. Клонируйте репозиторий:
```
git@github.com:Yana-K38/task_test_api_info_User.git
```
2. Создать файл .env в корне проекта и заполнить его всеми ключами:
```
SECRET=zyfgtnhjdf
```
3. Собрать контейнеры:
```
docker compose up -d --build
```
4. Заполнить БД тестовыми пользователями:
```
docker exec -it <id контейнера> python src/data/load_sql.py
```
После внесения тестовых пользователей будет достуаен пользователь:
```
"email": Admin@example.com
"username": admin
"password": admin
```

##### После запуска проекта, документация будет доступна по адресу:
```http://127.0.0.1:8000/docs/```
  
## Реализовано

* #### Получение списка всех пользователей:

Метод: GET

Маршрут: /users/

Фильтры:

filter_username: Фильтрация по имени пользователя (опционально).

filter_active: Фильтрация по активности (опционально).

sort_by: Поле для сортировки (опционально).

Возвращает список пользователей в формате JSON.

* #### Получение информации о пользователе по его ID:
  
Метод: GET

Маршрут: /users/{id}/

Возвращает информацию о пользователе в формате JSON.

* #### Получение информации о текущем пользователе (текущей сессии):

Метод: GET

Маршрут: /users/me

Возвращает информацию о текущем пользователе в формате JSON.

* #### Обновление информации о текущем пользователе:

Метод: PUT

Маршрут: /users/me

Принимает данные для обновления информации о пользователе.

Возвращает обновленную информацию о пользователе в формате JSON.

* #### Удаление текущего пользователя:

Метод: DELETE

Маршрут: /users/me

Удаляет текущего пользователя.

Возвращает сообщение об успешном удалении.

* #### Удаление пользователя по ID (только для суперпользователей или если ID совпадает с текущим пользователем):

Метод: DELETE

Маршрут: /users/{id}

Удаляет пользователя по указанному ID.

Возвращает сообщение об успешном удалении.

* #### Поиск пользователей по имени пользователя:

Метод: GET

Маршрут: /users/search_user

Принимает строку search_query для поиска пользователей.

Возвращает список найденных пользователей в формате JSON.
