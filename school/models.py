from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Subject(models.Model):
    name = models.CharField("Назва", max_length=100, unique=True)
    description = models.TextField("Опис", blank=True)

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предмети"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Teacher(models.Model):
    first_name = models.CharField("Ім'я", max_length=100)
    last_name = models.CharField("Прізвище", max_length=100)
    subject = models.ForeignKey(
        Subject, on_delete=models.PROTECT, related_name="teachers", verbose_name="Предмет"
    )

    class Meta:
        verbose_name = "Вчитель"
        verbose_name_plural = "Вчителі"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.subject})"


class Class(models.Model):
    name = models.CharField("Назва", max_length=20, unique=True)
    year = models.PositiveSmallIntegerField(
        "Рік навчання", validators=[MinValueValidator(1), MaxValueValidator(11)]
    )

    class Meta:
        verbose_name = "Клас"
        verbose_name_plural = "Класи"
        ordering = ["year", "name"]

    def __str__(self):
        return self.name


class Student(models.Model):
    first_name = models.CharField("Ім'я", max_length=100)
    last_name = models.CharField("Прізвище", max_length=100)
    school_class = models.ForeignKey(
        Class, on_delete=models.PROTECT, related_name="students", verbose_name="Клас"
    )

    class Meta:
        verbose_name = "Учень"
        verbose_name_plural = "Учні"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.school_class})"


class Schedule(models.Model):
    DAYS = [
        (1, "Понеділок"),
        (2, "Вівторок"),
        (3, "Середа"),
        (4, "Четвер"),
        (5, "П'ятниця"),
    ]

    day_of_week = models.PositiveSmallIntegerField("День тижня", choices=DAYS)
    start_time = models.TimeField("Година початку")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name="Предмет")
    school_class = models.ForeignKey(Class, on_delete=models.CASCADE, verbose_name="Клас")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="Вчитель")

    class Meta:
        verbose_name = "Заняття"
        verbose_name_plural = "Розклад"
        ordering = ["day_of_week", "start_time"]
        constraints = [
            models.UniqueConstraint(
                fields=["school_class", "day_of_week", "start_time"],
                name="unique_class_slot",
            ),
            models.UniqueConstraint(
                fields=["teacher", "day_of_week", "start_time"],
                name="unique_teacher_slot",
            ),
        ]

    def __str__(self):
        return (
            f"{self.get_day_of_week_display()} {self.start_time:%H:%M} — "
            f"{self.subject}, {self.school_class}, {self.teacher.last_name}"
        )


class Grade(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="grades", verbose_name="Учень"
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="grades", verbose_name="Предмет"
    )
    value = models.PositiveSmallIntegerField(
        "Оцінка", validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    date = models.DateField("Дата")

    class Meta:
        verbose_name = "Оцінка"
        verbose_name_plural = "Оцінки"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.student.last_name}: {self.subject} = {self.value} ({self.date})"
