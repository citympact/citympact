from django.urls import path

from . import views


app_name = 'mainApp' # Name space for the url links in templates
urlpatterns = [
    path('', views.index, name='index'),

    path('search', views.SearchView.as_view(), name='search'),

    path('project/<int:project_id>', views.projectDetail, name='projectDetail'),
    path('project/vote', views.VoteProject.as_view(), name='voteProject'),

    path('petition/<int:petition_id>', views.petitionDetail, \
        name='petitionDetail'),
    path('petition/vote', views.VotePetition.as_view(), name='votePetition'),
    path('petition/add', views.AddNewPetition.as_view(), name='addNewPetition'),
    path('add_vote_comment', views.AddVoteComment.as_view(),
        name='addVoteComment'),
]
