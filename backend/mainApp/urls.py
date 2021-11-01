from django.urls import path

from . import views


app_name = 'mainApp' # Name space for the url links in templates
urlpatterns = [
    path('', views.ProjectListView.as_view(), name='index'),
    path('project/add', views.addNewProject, name='addNewProject'),
    path('project/<int:project_id>', views.detail, name='detail'),
]
