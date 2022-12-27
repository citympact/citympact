from django.urls import include, path
from django.contrib.auth import views as auth_views

from django.contrib.auth.decorators import login_required
from . import views

from impact import settings


app_name = 'mainApp' # Name space for the url links in templates
if settings.PROJECT_STATUS.lower() == "TERMINATED".lower():

    urlpatterns = [
        path('', views.terminatedProjectIndex, name='index'),
        path('about.html', views.loginDisabledAbout, name='about'),
        path('contact.html', views.loginDisabledContact, name='contact')
    ]
else:
    urlpatterns = [
        path('', views.IndexView.as_view(), name='index'),

        path('search', views.SearchView.as_view(), name='search'),

        path('project/<int:project_id>', views.ProjectView.as_view(), name='projectDetail'),
        path('project/vote', views.VoteProject.as_view(), name='voteProject'),

        path('propositon/<int:proposition_id>', views.PropositionView.as_view(), \
            name='propositionDetail'),
        path('comment/add', views.AddNewCommentView.as_view(),
            name='addNewComment'),
        path('proposition/sign', views.SignProposition.as_view(), name='signProposition'),
        path('proposition/add', login_required(views.AddNewProposition.as_view()), name='addNewProposition'),
        path('add_vote_comment', views.AddVoteComment.as_view(),
            name='addVoteComment'),

        path('accounts/create', views.AccountsCreate.as_view(),
            name='account_create'),
        path('activate/<uid>/<token>', views.AccountsCreate.as_view(),
            name='activateAccount'),
        path('accounts/profile/',
            login_required(views.AccountsProfile.as_view()),
                name='accounts_profile'
        ),

        path('manager/', login_required(views.ManagerView.as_view()),
            name='manager'),
        path('about.html', views.AboutView.as_view(), name='about'),
        path('contact.html', views.ContactView.as_view(), name='contact')
    ]
