from django.contrib import admin

from tree.models import Course, CourseRelations

admin.site.register(Course)

admin.site.register(CourseRelations)
