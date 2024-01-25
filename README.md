# Foodgram 🍽️

Foodgram - это проект, предназначенный для публикации рецептов пользователей. В проекте можно добавлять рецепты в избранное, подписываться на пользователей, создавать свои списки покупок и скачивать их. Проект разработан с использованием следующих технологий:

- Backend: Django, Python, DRF, Docker
- Frontend: React
- Сервер: Nginx

## Автор

Проект создан Софией.

## Установка и запуск

Для установки и запуска проекта необходимо выполнить следующие шаги:

- Клонировать репозиторий с проектом: `git clone git@github.com:sofiya05/foodgram-project-react.git`
- Развернуть композицию docker командой: `docker compose -f docker-compose.production.yml`
- В контейнере загрузить данные из csv (идет сразу в проекте) командой: `docker compose -f docker-compose.production.yml exec backend python manage.py upload_csv`
- Сделать рестарт композиции командой: `docker compose -f docker-compose.production.yml restart`

## Аккаунт superuser

Для входа в админку проекта можно использовать следующие данные:

- Login: dev@yandex.ru
- Password: qwerty12345

## Ссылки

Проект доступен по следующим ссылкам:

- Сайт: [sonb.hopto.org](https://sonb.hopto.org)
- Админка: [sonb.hopto.org/admin](https://sonb.hopto.org/admin/)
- API: [sonb.hopto.org/api](https://sonb.hopto.org/api/)
