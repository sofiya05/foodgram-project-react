![main workflow](https://github.com/sofiya05/foodgram-project-react/actions/workflows/main.yml/badge.svg)

# Foodgram

Foodgram - это проект, предназначенный для публикации рецептов пользователей. В проекте можно добавлять рецепты в избранное, подписываться на пользователей, создавать свои списки покупок и скачивать их. Проект разработан с использованием следующих технологий:

* Backend: Django, Python, DRF, Docker
* Frontend: React
* Сервер: Nginx

## Автор

Проект создан Софией.

## Установка и настройка

Для установки и запуска проекта выполните следующие шаги:

1. Склонируйте репозиторий проекта: `git clone git@github.com:sofiya05/foodgram-project-react.git`
2. Разверните композицию Docker с помощью следующей команды: `docker compose -f docker-compose.production.yml`
3. Загрузите данные из CSV-файла в контейнер (включено в проект) с помощью следующей команды: `docker compose -f docker-compose.production.yml exec backend python manage.py upload_csv`
4. Перезапустите композицию с помощью следующей команды: `docker compose -f docker-compose.production.yml restart`

## Конфигурация файла .env

Заполните файл `.env` следующей информацией:

```plaintext
SECRET_KEY=django-insecure-<ваш-секретный-ключ>
DEBUG=True
ALLOWED_HOSTS=<ваши-хосты>
POSTGRES_USER=<ваш-пользователь-postgres>
POSTGRES_PASSWORD=<ваш-пароль-postgres>
POSTGRES_DB=foodgram
DB_HOST=db
DB_PORT=5432
POSTGRES=True
```

Замените `<ваш-секретный-ключ>`, `<ваш-пользователь-postgres>` `<ваши-хосты> (через , без пробелов)` и `<ваш-пароль-postgres>` на свои значения. Если вы предпочитаете использовать SQLite, установите `POSTGRES=False`. Обязательно сохраните файл `.env` в безопасном месте и не передавайте чувствительную информацию.

## Ссылки

Проект доступен по следующим ссылкам:

* Сайт: [sonb.hopto.org](https://sonb.hopto.org/)
* Админка: [sonb.hopto.org/admin/](https://sonb.hopto.org/admin/)
* API: [sonb.hopto.org/api/](https://sonb.hopto.org/api/)
* Документация: [sonb.hopto.org/api/docs/](https://sonb.hopto.org/api/docs/)
