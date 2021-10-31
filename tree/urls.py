from django.urls import path

from . import views

urlpatterns = [
    path('', views.tree, name='tree'),
    path('<int:course_id>', views.get_course, name='course'),
    path('add', views.add_sections_and_topics, name='add_sections_topics'),
    path('courses', views.courses_from_edu, name='courses from eduwiki'),
]
