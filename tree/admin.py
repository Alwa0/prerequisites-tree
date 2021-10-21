from django.contrib import admin

from tree.models import Course, CourseRelations, Section, Topic

admin.site.register(Course)

admin.site.register(CourseRelations)

admin.site.register(Section)

admin.site.register(Topic)
