<h1 align="center" style="font-size: 3em;">Анализатор страниц</h1>

### Hexlet tests and linter status:
[![Actions Status](https://github.com/Maxcosanostra/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/Maxcosanostra/python-project-83/actions)

[![Maintainability](https://api.codeclimate.com/v1/badges/1e01adc153c0c40755c1/maintainability)](https://codeclimate.com/github/Maxcosanostra/python-project-83/maintainability)

[![CI](https://github.com/Maxcosanostra/python-project-83/actions/workflows/ci.yml/badge.svg)](https://github.com/Maxcosanostra/python-project-83/actions/workflows/ci.yml)

Ссылка на домен:
https://python-project-83-gidc.onrender.com/


---
### Описание
Анализатор страниц – это веб-приложение, разработанное с использованием Flask, которое позволяет пользователям быстро и бесплатно проверять веб-сайты на SEO-пригодность.

Что же такое SEO-пригодность? SEO (Search Engine Optimization) – это оптимизация сайта для поисковых систем. Она включает в себя правильное использование HTML тегов, таких как 
h1, title, и meta name="description" content="...". Правильно структурированные теги позволяют поисковым системам понять основную тему страницы и эффективно отображать её в 
результатах поиска по соответствующим запросам.

Хотите, чтобы ваш сайт был в топе результатов поисковых систем? Следуйте этим принципам!


---

### Содержание

* Добавление URL для последующего анализа
* Анализ добавленного URL на SEO-пригодность
* История добавленных URL с кратким содержанием

---

### Ссылки

| Инструменты | Описание |
|----------|----------|
| [Poetry](https://python-poetry.org/) | Инструмент для управления зависимостями и создания виртуальных окружений в проектах на Python. |
| [Flask](https://flask.palletsprojects.com/en/3.0.x/) | Фреймворк для разработки веб-приложений. |
| [PostgreSQL](https://www.postgresql.org/) | Система управления базами данных. |
| [Gunicorn](https://gunicorn.org/) | WSGI HTTP-сервер для развертывания приложения в продакшене. |
| [Bootstrap](https://getbootstrap.com/) | CSS-фреймворк для создания адаптивных веб-приложений в современном дизайне. |
| [BeautifulSoup](https://pypi.org/project/beautifulsoup4/) | Библиотека для парсинга HTML и извлечения данных с веб-страниц. |

---

### Установка

1. Склонируйте репозиторий по ссылке:
   ```sh
   git clone https://github.com/Maxcosanostra/python-project-83
   ```

2. Установите зависимости:
   ```sh
   make install
   ```

3. Создайте .env файл и настройте структуру, как показано в примере .env.example:
   ```sh
   SECRET_KEY=ваш_секретный_ключ
   DATABASE_URL=postgresql://пользователь:пароль@localhost:5432/ваша_база_данных
   ```

4. Запустите приложение на локальном сервере:
   ```sh
   make dev
   ```

5. Запустите приложение на продакшн сервере:
   ```sh
   make start
   ```
---

Проект выполнен благодаря прохождению практики в Hexlet.io под руководством Рафаэля Мухаметшина

С Уважением, MaxCosaNostra
