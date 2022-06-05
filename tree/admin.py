from django.contrib import admin

from tree.models import Course, CourseRelations, Category

admin.site.register(Course)

admin.site.register(CourseRelations)

admin.site.register(Category)
