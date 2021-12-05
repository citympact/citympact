from django.urls import include, path
from django.contrib.auth import views as auth_views

from django.contrib.auth.decorators import login_required

from . import views


app_name = 'mainApp' # Name space for the url links in templates
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),

    path('search', views.SearchView.as_view(), name='search'),

    path('project/<int:project_id>', views.ProjectView.as_view(), name='projectDetail'),
    path('project/vote', views.VoteProject.as_view(), name='voteProject'),

    path('petition/<int:petition_id>', views.PetitionView.as_view(), \
        name='petitionDetail'),
    path('petition/sign', views.SignPetition.as_view(), name='signPetition'),
    path('petition/add', views.AddNewPetition.as_view(), name='addNewPetition'),
    path('add_vote_comment', views.AddVoteComment.as_view(),
        name='addVoteComment'),

    path('accounts/create', views.AccountsCreate.as_view(),
        name='account_create'),
    path('activate/<token>', views.AccountsCreate.as_view(),
        name='activateAccount'),
    path('accounts/profile/', login_required(views.AccountsProfile.as_view()),
        name='accounts_profile'),
]
