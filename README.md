# Телефонная книга
### _Тестовое задание для участие в проекте "Любимовка"_

## Подготовка проекта
### Создать и активировать виртуальное окружение, установить зависимости:
```sh
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
## Переименовать файл .env.example (/project_dir/reference_book/reference_book/.env.example) в .env и указать в нем недостающую информацию:
Для генерации SECRET_KEY:
```sh
openssl rand -hex 32
```
Полученное значение копируем в .env

## Создать базу и применить миграции:
Из директории /project_dir/reference_book/ выполнить:
```sh
python manage.py migrate
```
## Запустить проект:
```sh
python manage.py runserver
```
### _Перед деплоем необходимо установить для переменной Debug значение False в /project_dir/reference_book/reference_book/settings.py_
