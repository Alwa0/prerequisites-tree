from django.urls import path

from . import views
from django.conf.urls import url
from rest_framework.documentation import include_docs_urls
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Portal API",
        default_version='v1',
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('docs/', include_docs_urls(title='Portal Api')),
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('<str:program>/<int:visible>', views.tree, name='tree'),
    path('<str:program>', views.tree, name='tree'),
    path('course/<str:course_name>', views.graph_for_course, name='graph for one course by name'),
    path('course_id/<str:course_id>', views.graph_for_course_id, name='graph for one course by id'),
    path('graph/<str:course_id>', views.graph_by_id, name='graph for one course by id'),
    path('show/<str:course_name>', views.show_graph_for_course, name='graph for one course visualization'),
    path('choose_prerequisites/', views.choose_program, name='choose program'),
    path('choose_prerequisites/<str:program>', views.choose_course, name='choose course'),
    path('choose_prerequisites/<str:program>/<str:course>', views.choose_prerequisites, name='choose prerequisites'),
    path('student_graph/', views.graph_for_student, name='graph for student')
]
