from django.urls import path

from . import views

urlpatterns = [
    path('', views.tree, name='tree'),
    path('course/<str:course_name>', views.graph_for_course, name='graph for one course'),
]
