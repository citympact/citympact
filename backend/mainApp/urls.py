from django.urls import path

from . import views


app_name = 'mainApp' # Name space for the url links in templates
urlpatterns = [
    path('', views.index, name='index'),
    path('project/add', views.addNewProject, name='addNewProject'),
    path('project/<int:project_id>', views.detail, name='detail'),
    path('project/vote', views.VoteProject.as_view(), name='voteProject'),
    path('petition/vote', views.VotePetition.as_view(), name='votePetition'),
]
