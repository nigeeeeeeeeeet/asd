# Система керування шкільним розкладом

Django-проєкт з консольним інтерфейсом.

## Запуск

```bash
pip install django
python manage.py makemigrations school
python manage.py migrate
python manage.py console
```

## Моделі

- `Subject` — назва (унікальна), опис
- `Teacher` — ім'я, прізвище, FK → `Subject`
- `Class` — назва (унікальна), рік навчання (1–11)
- `Student` — ім'я, прізвище, FK → `Class`
- `Schedule` — день тижня, година, FK → `Subject`, `Class`, `Teacher` (клас і вчитель не можуть мати два заняття в один слот)
- `Grade` — FK → `Student`, `Subject`, оцінка (1–12), дата

## Git

```bash
git init
printf 'db.sqlite3\n__pycache__/\n' > .gitignore
git checkout -b feature/models
git add . && git commit -m "Add models and console interface"
```
