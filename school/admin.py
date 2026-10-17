from django.contrib import admin

from .models import Class, Grade, Schedule, Student, Subject, Teacher

for model in (Subject, Teacher, Class, Student, Schedule, Grade):
    admin.site.register(model)
