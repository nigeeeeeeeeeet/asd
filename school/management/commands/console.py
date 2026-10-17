from datetime import date, datetime

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.db.models import ProtectedError

from school.models import Class, Grade, Schedule, Student, Subject, Teacher


def ask(prompt):
    return input(prompt).strip()


def pick(model, label):
    """Показує список об'єктів і повертає вибраний за номером (id) або None."""
    items = list(model.objects.all())
    if not items:
        print(f"  {label}: список порожній. Спочатку додайте записи.")
        return None
    for obj in items:
        print(f"  [{obj.pk}] {obj}")
    raw = ask(f"{label} (id): ")
    if not raw.isdigit():
        print("  Помилка: потрібен числовий id.")
        return None
    obj = model.objects.filter(pk=int(raw)).first()
    if obj is None:
        print(f"  Помилка: {label.lower()} з таким id не існує.")
    return obj


def save(obj):
    try:
        obj.full_clean()
        obj.save()
    except ValidationError as e:
        print("  Помилка валідації:", "; ".join(sum(e.message_dict.values(), [])))
        return False
    except IntegrityError:
        print("  Помилка: такий запис уже існує або порушено обмеження (зайнятий слот?).")
        return False
    print(f"  Збережено: {obj}")
    return True


def add_subject():
    name = ask("Назва: ")
    desc = ask("Опис: ")
    if Subject.objects.filter(name__iexact=name).exists():
        print("  Помилка: предмет з такою назвою вже існує.")
        return
    save(Subject(name=name, description=desc))


def edit_subject():
    obj = pick(Subject, "Предмет")
    if not obj:
        return
    name = ask(f"Нова назва [{obj.name}]: ") or obj.name
    desc = ask("Новий опис [Enter — залишити]: ") or obj.description
    if Subject.objects.filter(name__iexact=name).exclude(pk=obj.pk).exists():
        print("  Помилка: предмет з такою назвою вже існує.")
        return
    obj.name, obj.description = name, desc
    save(obj)


def delete_subject():
    obj = pick(Subject, "Предмет")
    if not obj:
        return
    try:
        obj.delete()
        print("  Видалено.")
    except ProtectedError:
        print("  Не можна видалити: до предмета прив'язані вчителі.")


def add_teacher():
    first, last = ask("Ім'я: "), ask("Прізвище: ")
    if not first or not last:
        print("  Помилка: ім'я та прізвище обов'язкові.")
        return
    subject = pick(Subject, "Предмет")
    if subject:
        save(Teacher(first_name=first, last_name=last, subject=subject))


def add_class():
    name = ask("Назва (напр. 7-А): ")
    year = ask("Рік навчання (1-11): ")
    if not year.isdigit():
        print("  Помилка: рік навчання має бути числом.")
        return
    if Class.objects.filter(name__iexact=name).exists():
        print("  Помилка: клас з такою назвою вже існує.")
        return
    save(Class(name=name, year=int(year)))


def edit_class():
    obj = pick(Class, "Клас")
    if not obj:
        return
    name = ask(f"Нова назва [{obj.name}]: ") or obj.name
    year = ask(f"Новий рік навчання [{obj.year}]: ") or str(obj.year)
    if not year.isdigit():
        print("  Помилка: рік навчання має бути числом.")
        return
    if Class.objects.filter(name__iexact=name).exclude(pk=obj.pk).exists():
        print("  Помилка: клас з такою назвою вже існує.")
        return
    obj.name, obj.year = name, int(year)
    save(obj)


def delete_class():
    obj = pick(Class, "Клас")
    if not obj:
        return
    try:
        obj.delete()
        print("  Видалено.")
    except ProtectedError:
        print("  Не можна видалити: у класі є учні.")


def add_student():
    first, last = ask("Ім'я: "), ask("Прізвище: ")
    if not first or not last:
        print("  Помилка: ім'я та прізвище обов'язкові.")
        return
    cls = pick(Class, "Клас")
    if cls:
        save(Student(first_name=first, last_name=last, school_class=cls))


def add_schedule():
    for num, title in Schedule.DAYS:
        print(f"  {num} — {title}")
    day = ask("День тижня (1-5): ")
    if not day.isdigit() or int(day) not in dict(Schedule.DAYS):
        print("  Помилка: день тижня має бути від 1 до 5.")
        return
    try:
        start = datetime.strptime(ask("Година початку (ГГ:ХХ): "), "%H:%M").time()
    except ValueError:
        print("  Помилка: формат часу ГГ:ХХ.")
        return
    subject = pick(Subject, "Предмет")
    if not subject:
        return
    cls = pick(Class, "Клас")
    if not cls:
        return
    teacher = pick(Teacher, "Вчитель")
    if not teacher:
        return
    if teacher.subject_id != subject.pk:
        print("  Попередження: вчитель викладає інший предмет.")
        if ask("Все одно зберегти? (т/н): ").lower() not in ("т", "y", "так"):
            return
    save(Schedule(day_of_week=int(day), start_time=start, subject=subject,
                  school_class=cls, teacher=teacher))


def add_grade():
    student = pick(Student, "Учень")
    if not student:
        return
    subject = pick(Subject, "Предмет")
    if not subject:
        return
    value = ask("Оцінка (1-12): ")
    if not value.isdigit():
        print("  Помилка: оцінка має бути числом.")
        return
    raw = ask("Дата (РРРР-ММ-ДД, Enter — сьогодні): ")
    try:
        d = datetime.strptime(raw, "%Y-%m-%d").date() if raw else date.today()
    except ValueError:
        print("  Помилка: формат дати РРРР-ММ-ДД.")
        return
    save(Grade(student=student, subject=subject, value=int(value), date=d))


def show_schedule():
    items = Schedule.objects.select_related("subject", "school_class", "teacher")
    if not items:
        print("  Розклад порожній.")
    for s in items:
        print(" ", s)


MENU = [
    ("Додати предмет", add_subject),
    ("Редагувати предмет", edit_subject),
    ("Видалити предмет", delete_subject),
    ("Додати вчителя", add_teacher),
    ("Додати клас", add_class),
    ("Редагувати клас", edit_class),
    ("Видалити клас", delete_class),
    ("Додати учня", add_student),
    ("Додати заняття в розклад", add_schedule),
    ("Додати оцінку", add_grade),
    ("Показати розклад", show_schedule),
]


class Command(BaseCommand):
    help = "Консольний інтерфейс керування шкільним розкладом"

    def handle(self, *args, **options):
        while True:
            print("\n=== Шкільний розклад ===")
            for i, (title, _) in enumerate(MENU, 1):
                print(f"{i:>2}. {title}")
            print(" 0. Вихід")
            choice = ask("Ваш вибір: ")
            if choice == "0":
                break
            if choice.isdigit() and 1 <= int(choice) <= len(MENU):
                MENU[int(choice) - 1][1]()
            else:
                print("  Невірний пункт меню.")
